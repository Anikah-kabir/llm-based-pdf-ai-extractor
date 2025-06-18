from fastapi import APIRouter, Depends
from app.models import PDFDocument
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user
from sqlmodel import Session

router = APIRouter()

@router.post("/")
def upload_pdf(data: dict, session: Session = Depends(get_db), current_user=Depends(get_current_user)):
    pdf = PDFDocument(**data, uploaded_by=current_user.id)
    session.add(pdf)
    session.commit()
    session.refresh(pdf)
    return pdf
