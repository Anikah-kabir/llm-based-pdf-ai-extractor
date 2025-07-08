from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.models import PDFDocument
from app.api.deps.db import get_session
from app.api.deps.auth import get_current_user
from sqlmodel import Session
from pathlib import Path
import uuid

router = APIRouter()

UPLOAD_DIR = Path("uploaded_pdfs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/")
def upload_pdf(data: dict):
    pass

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    unique_name = f"{uuid.uuid4()}.pdf"
    file_path = UPLOAD_DIR / unique_name

    with file_path.open("wb") as f:
        content = await file.read()
        f.write(content)

    return {"filename": unique_name, "msg": "PDF uploaded successfully"}
