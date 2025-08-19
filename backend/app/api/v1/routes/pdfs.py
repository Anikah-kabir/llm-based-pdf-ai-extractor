from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlmodel import Session, select
from pathlib import Path
from typing import Optional, List, Dict
import uuid
import asyncio
from app.api.deps.db import get_session
from app.core.config import get_settings
from app.models import PDFDocument, PDFChunk
from app.services.pdf_reader import extract_full_text
from app.services.chunking import smart_chunk_text
#from app.services.doc_type import auto_detect_doc_type
from app.services.doc_type_detector import detect_doc_type
from app.services.weaviate_store import init_schema, store_pdf_in_weaviate, search_chunks, get_weaviate_client
from app.services.llm_extractor import process_chunk_with_llm, generate_llm_response
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update

settings = get_settings()
router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def truncate_for_upload(pages: list[dict]) -> str:
    # Build a small text for extraction (avoid long-token errors)
    text = "\n".join([p["text"] for p in pages])[:settings.max_text_chars_upload]
    return text

@router.get("/")
async def list_pdfs(session: Session = Depends(get_session)):

    client = get_weaviate_client()
    #client.collections.delete("PDFChunks")
    schema = client.collections.list_all(simple=False)
    client.close()
    print("schema")
    print(schema)

    pdfs = session.exec(select(PDFDocument)).all()
    return [{"id":pdf.id, "filename": pdf.filename, "upload_time": pdf.upload_time} for pdf in pdfs]

@router.get("/{id}")
async def get_pdf_detail(id: uuid.UUID, session: Session = Depends(get_session)):
    pdf = session.exec(select(PDFDocument).where(PDFDocument.id == id)).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    return {
        "id": str(pdf.id),
        "filename": pdf.filename,
        "doc_type": pdf.doc_type,
        "extracted_data": pdf.extracted_data,
        "status": pdf.status
    }

@router.post("/rag/query")
async def rag_query(
    question: str,
    pdf_id: str = None,
    session: Session = Depends(get_session)
):
    filters = []

    if pdf_id:
        pdf_doc = session.exec(
            select(PDFDocument).where(PDFDocument.id == pdf_id)
        ).first()
        if not pdf_doc:
            raise HTTPException(status_code=404, detail="PDF not found")
        filters.append(("doc_type", pdf_doc.doc_type))
        filters.append(("pdf_id", str(pdf_doc.id)))

    hits = search_chunks(question, filters=filters, limit=6)
    if not hits:
        return {"result": {"answer": "No relevant information found", "source": None, "confidence": 0.0}}

    contexts = [f"[Source: {h['filename']}, page {h['page_no']}] {h['chunk']}" for h in hits]

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

@router.post("/upload")
async def upload_and_index_pdf(
    file: UploadFile = File(...),
    doc_type: str | None = Form(None),
    goal: str | None = Form(default=None),
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
 
    init_schema()
    # Store initial chunks in both databases
    initial_chunks = [{
        **chunk,
        "pdf_id": str(pdf_doc.id),
        "filename": file.filename,
        "doc_type": doc_type
    } for chunk in enhanced_chunks]
    store_pdf_in_weaviate(str(pdf_doc.id), file.filename, enhanced_chunks, doc_type)
    upsert_pdf_chunks(session, initial_chunks)

    # Background task for remaining chunks
    if len(chunks) > 3:
        background_tasks.add_task(
            process_remaining_chunks,
            pdf_id=str(pdf_doc.id),
            chunks=chunks[3:],
            doc_type=doc_type,
            filename=file.filename
        )

    return {
        "message": "PDF upload started",
        "pdf_id": str(pdf_doc.id),
        "processed_chunks": len(enhanced_chunks),
        "total_chunks": len(chunks),
        "doc_type": doc_type,
        "detection": detection_reason,
        "status": "processing" if len(chunks) > 3 else "processed"
    }
async def process_remaining_chunks(
    pdf_id: str, 
    chunks: List[Dict], 
    doc_type: str, 
    filename: str,
    db: Session = Depends(get_session)
):
    enhanced_chunks = []
    
    for i in range(0, len(chunks), 5):  # Process in batches of 5
        batch = chunks[i:i+5]
        processed_batch = []
        
        for chunk in batch:
            try:
                processed = await process_chunk_with_llm(chunk, doc_type)
                processed_batch.append(processed)
            except Exception as e:
                processed_batch.append({
                    **chunk,
                    "processed": False,
                    "llm_error": str(e)
                })
        
        # Store in both databases
        store_pdf_in_weaviate(pdf_id, filename, processed_batch, doc_type)
        upsert_pdf_chunks(db, [{
            **chunk,
            "pdf_id": pdf_id,
            "filename": filename,
            "doc_type": doc_type
        } for chunk in processed_batch])
        
        await asyncio.sleep(1)  # Rate limiting

    # Update main document status
    db.execute(
        update(PDFDocument)
        .where(PDFDocument.id == pdf_id)
        .values(status="processed")
    )
    db.commit()

def upsert_pdf_chunks(db: Session, chunks: List[Dict]):
    """Bulk upsert chunks with conflict handling"""
    stmt = insert(PDFChunk).values([
        {
            "pdf_id": chunk["pdf_id"],
            "filename": chunk["filename"],
            "doc_type": chunk["doc_type"],
            "chunk_num": chunk["chunk_num"],
            "approx_page": chunk["approx_page"],
            "char_count": chunk["char_count"],
            "word_count": chunk["word_count"],
            "token_estimate": chunk["tokens"],
            "has_tables": chunk["has_tables"],
            "has_figures": chunk["has_figures"],
            "content": chunk["content"],
            "llm_analysis": chunk.get("llm_analysis"),
            "processing_metadata": {
                "processed": chunk.get("processed", False),
                "error": chunk.get("llm_error")
            }
        }
        for chunk in chunks
    ])
    
    stmt = stmt.on_conflict_do_update(
        index_elements=['pdf_id', 'chunk_num'],
        set_={
            'content': stmt.excluded.content,
            'llm_analysis': stmt.excluded.llm_analysis,
            'processing_metadata': stmt.excluded.processing_metadata
        }
    )
    
    db.execute(stmt)
    db.commit()