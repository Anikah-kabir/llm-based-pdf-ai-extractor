import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlmodel import SQLModel, Field

class PDFChunk(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    pdf_id: uuid.UUID = Field(
        foreign_key="pdfdocument.id", 
        index=True,
        nullable=False
    )
    filename: str = Field(nullable=False)
    doc_type: str = Field(nullable=False)
    chunk_num: int = Field(nullable=False)
    approx_page: int = Field(nullable=False)
    char_count: int = Field(nullable=False)
    word_count: int = Field(nullable=False)
    token_estimate: int = Field(nullable=False)
    has_tables: bool = Field(default=False, nullable=False)
    has_figures: bool = Field(default=False, nullable=False)
    content: str = Field(nullable=False)
    chunk_meta: Dict[str, Any] = Field(
        default_factory=dict,
        nullable=False,
        sa_type=JSONB
    )
    
    llm_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        nullable=True,
        sa_type=JSONB
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": func.now()}
    )