from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from app.models import PDFDocument
from app.api.deps.db import get_session
from app.api.deps.auth import get_current_user
from typing import Optional
from app.services.pdf_reader import extract_text_from_pdf
from app.services.llm_extractor import extract_structured_data_from_pdf_text, PromptRequest,detect_goal_from_text, rule_based_goal_detection
from sqlmodel import Session, select
from pathlib import Path
import uuid

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_TEXT_LENGTH = 12000
router = APIRouter()

@router.get("/")
def list_pdfs(session: Session = Depends(get_session)):
    pdfs = session.exec(select(PDFDocument)).all()
    return [{"id":pdf.id, "filename": pdf.filename, "upload_time": pdf.upload_time} for pdf in pdfs]

@router.get("/{id}")
def get_pdf_detail(id: uuid.UUID, session: Session = Depends(get_session)):
    pdf = session.exec(select(PDFDocument).where(PDFDocument.id == id)).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    return {
        "id": pdf.id,
        "filename": pdf.filename,
        "extracted_data": pdf.extracted_data
    }

@router.post("/upload")
async def upload_and_extract_pdf(
    file: UploadFile = File(...),
    doc_type: str = Form("default"),
    goal: Optional[str] = Form(None),
    session: Session = Depends(get_session)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = await file.read()
    try:
        text = extract_text_from_pdf(content)
        if len(text) > MAX_TEXT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail="PDF is too long. Please upload a smaller document (max 12,000 characters)."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")
    
    

    goal = goal or detect_goal_from_text(text)
    if not goal:
        try:
            goal = detect_goal_from_text(text)
        except Exception as e:
            goal = None
    try:
        req = PromptRequest(text=text, goal=goal, doc_type=doc_type)
        result = extract_structured_data_from_pdf_text(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting structured data: {str(e)}")

    unique_name = f"{uuid.uuid4()}.pdf"
    file_path = UPLOAD_DIR / unique_name
    with file_path.open("wb") as f:
        f.write(content)

    # save structured_data to the DB
    doc = PDFDocument(
        filename=file.filename,
        extracted_text=text,
        extracted_data=result["structured_data"],
        doc_type=doc_type,
        status="processed",
        prompt_used=result["prompt_used"],
        llm_used=result["llm_used"]
        
    )

    try:
        session.add(doc)
        session.commit()
        session.refresh(doc)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
 
    return {
        "filename": unique_name,
        "message": "PDF uploaded and processed successfully",
        "extracted_data": result["structured_data"]
    }
