from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlmodel import Session, select, desc
from pathlib import Path
from typing import Optional, List, Dict
import uuid
import asyncio
from app.api.deps.db import get_session
from app.core.config import get_settings
from app.models import PDFDocument, PDFDetailResponse, PDFChunk
from app.services.pdf_reader import extract_full_text
from app.services.chunking import smart_chunk_text, truncate_for_upload
#from app.services.doc_type import auto_detect_doc_type
from app.services.doc_type_detector import detect_doc_type
from app.services.weaviate_store import init_schema, store_pdf_in_weaviate, search_chunks, get_weaviate_client
from app.services.llm_extractor import process_chunk_with_llm, generate_llm_response
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update
import re, json
import logging
from datetime import datetime
from contextlib import contextmanager

settings = get_settings()
router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.get("/")
async def list_pdfs(session: Session = Depends(get_session)):

    client = get_weaviate_client()
    #client.collections.delete("PDFChunks")
    schema = client.collections.list_all(simple=False)
    client.close()
    #print("schema")
    #print(schema)

    pdfs = session.exec(
        select(PDFDocument).order_by(desc(PDFDocument.upload_time))
    ).all()
    return [{"id":pdf.id, "filename": pdf.filename, "upload_time": pdf.upload_time} for pdf in pdfs]


def extract_json_from_string(text: str):
    try:
        match = re.search(r"```json([\s\S]*?)```", text)
        if match:
            return json.loads(match.group(1))  # valid JSON extracted
    except Exception as e:
        print("JSON parse failed:", e)
    return text

@router.get("/{id}")
async def get_pdf_detail(id: uuid.UUID, session: Session = Depends(get_session), response_model=PDFDetailResponse):
    pdf = session.exec(select(PDFDocument).where(PDFDocument.id == id)).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    cleaned_data =  {
        "id": str(pdf.id),
        "filename": pdf.filename,
        "doc_type": pdf.doc_type,
        "extracted_data": extract_json_from_string(pdf.extracted_data),
        "status": pdf.status
    }
    return PDFDetailResponse(**cleaned_data)
    
@router.post("/rag/query")
async def rag_query(
    question: str,
    pdf_id: str = None,
    session: Session = Depends(get_session)
):
    filters = []

    if pdf_id:
        try:
            pdf_doc = session.exec(
                select(PDFDocument).where(PDFDocument.id == pdf_id)
            ).first()
            if pdf_doc:
                filters.append(("doc_type", pdf_doc.doc_type))
                filters.append(("pdf_id", str(pdf_doc.id)))
        except Exception as e:
            logging.error(f"Error fetching PDF document: {e}")
            # Continue without filters if there's an error

    try:
        hits = search_chunks(question, filters=filters, limit=6)
    except Exception as search_error:
        logging.error(f"Search failed: {search_error}")
        hits = []

    if not hits:
        return {
            "result": {
                "answer": "No relevant information found in the knowledge base.",
                "source": None,
                "confidence": 0.0
            },
            "retrieved_chunks": []
        }

    try:
        contexts = [f"[Source: {h['filename']}, page {h.get('page_no', 'N/A')}] {h['content']}" for h in hits]

        structured_prompt = f"""
Answer the question strictly using the provided context. 
Return JSON with: answer, source, confidence (0 to 1).

Context:
{chr(10).join(contexts)}

Question: {question}
JSON:
"""
        llm_output = generate_llm_response(structured_prompt)
        
        return {
            "result": llm_output,
            "retrieved_chunks": hits
        }
        
    except Exception as e:
        logging.error(f"LLM processing failed: {e}")
        return {
            "result": {
                "answer": "Error processing your query. Please try again.",
                "source": None,
                "confidence": 0.0
            },
            "retrieved_chunks": hits
        }

@router.get("/{pdf_id}/chunks", response_model=List[Dict])
def get_pdf_chunks(
    pdf_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session)
):
    chunks = db.query(PDFChunk)\
        .filter(PDFChunk.pdf_id == pdf_id)\
        .order_by(PDFChunk.chunk_num)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [ {
        "id": chunk.id,
        "chunk_num": chunk.chunk_num,
        "page": chunk.approx_page,
        "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
        "char_count": chunk.char_count,
        "processed": chunk.chunk_meta.get("processed", False),
        "has_analysis": bool(chunk.llm_analysis)
    } for chunk in chunks]

@router.post("/upload")
async def upload_and_index_pdf(
    file: UploadFile = File(...),
    doc_type: str | None = Form(None),
    session: Session = Depends(get_session),
    background_tasks: BackgroundTasks = None
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = await file.read()
    try:
        full_text = extract_full_text(content)
        chunks = smart_chunk_text(full_text)
    except Exception as e:
        raise HTTPException(500, f"Error processing PDF: {e}")

    detection_reason = "provided"
    if not doc_type:
        doc_type, detection_reason = detect_doc_type(full_text)
    
    init_schema()

    # # Process first 3 chunks in parallel for quick response
    enhanced_chunks = []
    processing_errors = []
    # Process chunks in batches (first batch synchronously for quick response)
    first_batch = chunks[:3]
    for chunk in first_batch:
        try:
            processed = await process_chunk_with_llm(chunk, doc_type)
            enhanced_chunks.append(processed)
        except Exception as e:
           processing_errors.append(f"Chunk {chunk['chunk_num']}: {str(e)}")
           enhanced_chunks.append({**chunk, "processed": False})

    
    # DB record
    pdf_doc = PDFDocument(
        filename=file.filename,
        extracted_text=truncate_for_upload(full_text),
        extracted_data={
            "initial_chunks": enhanced_chunks[:3],
            "total_chunks": len(chunks),
            "processing_errors": processing_errors
        },
        doc_type=doc_type,
        status= "processing" if len(chunks) > 3 else "processed",
        is_public=True
    )

    try:
        session.add(pdf_doc)
        session.commit()
        session.refresh(pdf_doc)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Persist the file
    file_path = UPLOAD_DIR / f"{pdf_doc.id}.pdf"
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        # Create initial chunks with metadata
        initial_chunks = [{
            **chunk,
            "pdf_id": str(pdf_doc.id),
            "filename": file.filename,
            "doc_type": doc_type
        } for chunk in enhanced_chunks]

        logging.info(f"Processing {len(initial_chunks)} initial chunks")

        #Store in Weaviate
        try:
            store_pdf_in_weaviate(str(pdf_doc.id), file.filename, enhanced_chunks, doc_type)
            logging.info("Successfully stored in Weaviate")
        except Exception as weaviate_error:
            logging.error(f"Weaviate storage failed: {weaviate_error}")
            raise HTTPException(500, f"Weaviate storage failed: {weaviate_error}")

        # Store in PostgreSQL
        logging.info("Chunk stored in PostgreSQL")
        print("Chunk stored in PostgreSQL")
        try:
            upsert_pdf_chunks(session, initial_chunks)
            logging.info("Successfully stored in PostgreSQL")
        except Exception as postgres_error:
            print(f"PostgreSQL storage failed: {postgres_error}")
            logging.error(f"PostgreSQL storage failed: {postgres_error}")
            session.rollback()
            raise HTTPException(500, f"Error processing PDF: {postgres_error}")
            # Continue with background tasks

        # Schedule background processing for remaining chunks
        remaining_count = len(chunks) - 3
        if remaining_count > 0:
            try:
                background_tasks.add_task(
                    process_remaining_chunks,
                    pdf_id=str(pdf_doc.id),
                    chunks=chunks[3:],
                    doc_type=doc_type,
                    filename=file.filename
                )
                logging.info(f"Scheduled {remaining_count} chunks for background processing")
            except Exception as bg_error:
                print(f"Background task scheduling failed: {bg_error}")
                logging.error(f"Background task scheduling failed: {bg_error}")

    except Exception as main_error:
        print(f"Critical error in chunk storage: {main_error}")
        logging.error(f"Critical error in chunk storage: {main_error}")
        raise

    return {
        "message": "PDF upload started",
        "filename": str(file.filename),
        "pdf_id": str(pdf_doc.id),
        "processed_chunks": len(enhanced_chunks),
        "total_chunks": len(chunks),
        "doc_type": doc_type,
        "detection": detection_reason,
        "status": "processing" if len(chunks) > 3 else "processed"
    }


@contextmanager
def get_db_session():
    """Get database session with context manager"""
    db = next(get_session())
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

async def process_remaining_chunks(
    pdf_id: str, 
    chunks: List[Dict], 
    doc_type: str, 
    filename: str,
):
    with get_db_session() as db:
        try:
            all_processed_chunks = []
            
            for i in range(0, len(chunks), 5):  # Process in batches of 5
                batch = chunks[i:i+5]
                # Process entire batch in parallel
                try:
                    processed_batch = await process_batch_parallel(batch, doc_type)
                    all_processed_chunks.extend(processed_batch)
                except Exception as batch_error:
                    logging.error(f"Batch processing failed: {batch_error}")
                    # Fallback: process failed chunks individually
                    for chunk in batch:
                        try:
                            processed = await process_chunk_with_llm(chunk, doc_type)
                            all_processed_chunks.append(processed)
                        except Exception as e:
                            all_processed_chunks.append({
                                **chunk,
                                "processed": False,
                                "llm_error": str(e)
                            })
                
                await asyncio.sleep(0.5) 
                # Store in both databases

                store_pdf_in_weaviate(pdf_id, filename, processed_batch, doc_type)
                try:
                    upsert_pdf_chunks(db, [{
                        **chunk,
                        "pdf_id": pdf_id,
                        "filename": filename,
                        "doc_type": doc_type
                    } for chunk in all_processed_chunks])
                    
                    # Update main document status
                    db.execute(
                        update(PDFDocument)
                        .where(PDFDocument.id == pdf_id)
                        .values(status="processed")
                    )
                    db.commit()
                    
                except Exception as e:
                    db.rollback()
                    logging.error(f"Failed to store processed chunks: {e}")
                    raise
            # Update main document status
            db.execute(
                update(PDFDocument)
                .where(PDFDocument.id == pdf_id)
                .values(status="processed")
            )
            db.commit()
        except Exception as e:
            db.rollback()
            db.execute(
                update(PDFDocument)
                .where(PDFDocument.id == pdf_id)
                .values(status="failed", error=str(e))
            )
            db.commit()
            logging.error(f"Background task failed: {e}")

def upsert_pdf_chunks(db: Session, chunks: List[Dict]):
    """Bulk upsert chunks with conflict handling - optimized"""
    if not chunks:
        return
    
    # Prepare data for bulk insert
    values_list = []
    for chunk in chunks:
        values_list.append({
            "pdf_id": chunk["pdf_id"],
            "filename": chunk["filename"],
            "doc_type": chunk["doc_type"],
            "chunk_num": chunk["chunk_num"],
            "approx_page": chunk["approx_page"],
            "char_count": chunk["char_count"],
            "word_count": chunk["word_count"],
            "token_estimate": chunk["token_estimate"],
            "has_tables": chunk["has_tables"],
            "has_figures": chunk["has_figures"],
            "content": chunk["content"],
            "llm_analysis": chunk.get("llm_analysis"),
            "chunk_meta": {
                "processed": chunk.get("processed", False),
                "error": chunk.get("llm_error")
            },
            "created_at": datetime.utcnow()
        })
    
    stmt = insert(PDFChunk).values(values_list)
    
    stmt = stmt.on_conflict_do_update(
        index_elements=['pdf_id', 'chunk_num'],
        set_={
            'content': stmt.excluded.content,
            'llm_analysis': stmt.excluded.llm_analysis,
            'chunk_meta': stmt.excluded.chunk_meta
        }
    )
    
    db.execute(stmt)


async def process_batch_parallel(batch: List[Dict], doc_type: str) -> List[Dict]:
    """
    Process a batch of chunks in parallel using OpenAI API
    """
    tasks = []
    for chunk in batch:
        # Create a task for each chunk
        task = process_chunk_with_llm(chunk, doc_type)
        tasks.append(task)
    
    # Process all chunks in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results and handle exceptions
    processed_batch = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Handle error for this chunk
            logging.error(f"Error processing chunk {i}: {result}")
            processed_batch.append({
                **batch[i],
                "processed": False,
                "llm_error": str(result)
            })
        else:
            # Successful processing
            processed_batch.append(result)
    
    return processed_batch