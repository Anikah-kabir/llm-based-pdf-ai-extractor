from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import uuid
import sqlalchemy as sa

if TYPE_CHECKING:
    from .address import Address
    from .user import User

class PDFDocumentTagLink(SQLModel, table=True):
    __tablename__ = "pdfdocumenttaglink"
    pdf_document_id: uuid.UUID = Field(default_factory=uuid.uuid4, foreign_key="pdf_documents.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tags.id", primary_key=True)

class TagBase(SQLModel):
    name: str = Field(sa_column=sa.Column(sa.String, index=True, unique=True, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=sa.Column(sa.Text, nullable=True))

class Tag(TagBase, table=True):
    __tablename__ = "tags"

    id: int = Field(default=None, primary_key=True)
    pdf_documents: list["PDFDocument"] = Relationship(back_populates="tags", link_model=PDFDocumentTagLink)


class PDFDocument(SQLModel, table=True):   
    __tablename__ = "pdf_documents"
 
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    filename: str = Field(sa_column=sa.Column(sa.String, nullable=False)) # Not null string

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

    # Many-to-many relationship with Tag
    tags: List[Tag] = Relationship(back_populates="pdf_documents", link_model=PDFDocumentTagLink)
    # Optional relationship to Address
    # Address ID is integer
    address_id: Optional[int] = Field(default=None,foreign_key="addresses.id")
    address: Optional[Address] = Relationship(back_populates="pdf_documents")

    # Uploaded by (User)
    uploaded_by_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, foreign_key="users.id")    
    uploaded_by: Optional[User] = Relationship(back_populates="pdf_documents")

