from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# Shared Base
class PDFDocumentBase(BaseModel):
    filename: str
    uploaded_by: str
    extracted_text: Optional[str] = None
    meta: Optional[str] = None
    tags: List[str] = []
    status: Optional[str] = "pending"
    extracted_data: Optional[dict] = None
    llm_used: Optional[str] = None
    prompt_used: Optional[str] = None
    address_id: Optional[int] = None  # Optional FK link
    is_public: bool = False

# For creating a new document
class PDFDocumentCreate(PDFDocumentBase):
    pass

# For updating an existing document
class PDFDocumentUpdate(BaseModel):
    filename: Optional[str] = None
    extracted_text: Optional[str] = None
    meta: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    extracted_data: Optional[dict] = None
    llm_used: Optional[str] = None
    prompt_used: Optional[str] = None
    address_id: Optional[int] = None
    is_public: bool
    uploaded_by_id: int

# For returning a document
class PDFDocumentResponse(PDFDocumentBase):
    id: UUID
    upload_time: datetime

    class Config:
        orm_mode = True
