from fastapi import APIRouter, Query, Depends
from sqlmodel import Session, select
from app.api.deps.db import get_session
from app.models import PDFChunk
from sqlalchemy import func
from pydantic import BaseModel
from typing import List

router = APIRouter()


class PDFChunkStats(BaseModel):
    filename: str
    chunk_count: int

@router.get("/")
async def list_pdfs(
    session: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=50, description="Number of recent documents to return"),
    response_model=List[PDFChunkStats]               
):
    result = session.exec(
            select(PDFChunk.filename, func.count(PDFChunk.pdf_id))
            .group_by(PDFChunk.filename)
            .limit(limit)
        ).all()
    stats = [PDFChunkStats(filename=row[0], chunk_count=row[1]) for row in result]
    return stats