from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING, Union, List, Dict, Any
from datetime import datetime
import uuid
import sqlalchemy as sa
from pydantic import BaseModel

if TYPE_CHECKING:
    from .address import Address
    from .user import User

# class PDFDocumentTagLink(SQLModel, table=True):
#     pdfdocument_id: uuid.UUID = Field(foreign_key="pdfdocument.id", primary_key=True)
#     tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)

# class TagBase(SQLModel):
#     name: str = Field(sa_column=sa.Column(sa.String, index=True, unique=True, nullable=False))
#     description: Optional[str] = Field(default=None, sa_column=sa.Column(sa.Text, nullable=True))

# class Tag(TagBase, table=True):
#     id: int = Field(default=None, primary_key=True)
#     pdfdocuments: list["PDFDocument"] = Relationship(back_populates="tags", link_model=PDFDocumentTagLink)

class PDFDocumentBase(SQLModel):
    filename: str = Field(sa_column=sa.Column(sa.String, nullable=False)) # Not null string
    doc_type: str = Field(default="default", sa_column=sa.Column(sa.String, nullable=False))
    upload_time: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False)
    )
    extracted_text: Optional[str] = Field(
        default=None,
        sa_column=sa.Column(sa.Text, nullable=True)
    )
    meta: Optional[str] = Field(default=None, sa_column=sa.Column(sa.Text, nullable=True))
    extracted_data: Optional[dict] = Field(default=None, sa_column=sa.Column(sa.JSON, nullable=True))
    llm_used: Optional[str] = Field(default=None, sa_column=sa.Column(sa.String, nullable=True))
    prompt_used: Optional[str] = Field(default=None, sa_column=sa.Column(sa.String, nullable=True))
    
    status: str = Field(
        default="pending",
        sa_column=sa.Column(sa.String, nullable=False)
    )  # Options: pending, processed, failed
    is_public: bool = Field(default=False, sa_column=sa.Column(sa.Boolean, nullable=False))
    # Uploaded by (User)
    uploaded_by_id: uuid.UUID | None = Field(foreign_key="user.id")    

class PDFDocument(PDFDocumentBase, table=True):    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    #uploaded_by: Optional[User] = Relationship(back_populates="pdfdocuments")


class PDFDetailResponse(BaseModel):
    id: str
    filename: str
    doc_type: str
    extracted_data: Union[str, Dict[str, Any], List[Dict[str, Any]]]
    status: str

class PDFDocumentPublic(PDFDocumentBase):
    id: int


class PDFDocumentCreate(PDFDocumentBase):
    pass

