from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class PDFChunkBase(BaseModel):
    pdf_id: str
    filename: str
    doc_type: str
    chunk_num: int
    approx_page: int
    char_count: int
    word_count: int
    token_estimate: int
    has_tables: bool
    has_figures: bool
    content: str
    llm_analysis:Dict[str, Any]
    chunk_meta: Dict[str, Any]

class PDFChunkCreate(PDFChunkBase):
    pass

class PDFChunk(PDFChunkBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PDFChunkUpdate(BaseModel):
    doc_type: Optional[str] = None
    chunk_meta: Optional[Dict[str, Any]] = None