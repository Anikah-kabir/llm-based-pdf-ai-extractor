from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
import sqlalchemy as sa
import uuid

if TYPE_CHECKING:
    from app.models import User, PDFDocument

class Address(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    name: Optional[str] = None  # Optional: "Home", "Work", etc.
    street: Optional[str] = Field(nullable=True)
    city: Optional[str] = Field(nullable=True)
    state: Optional[str] = Field(nullable=True)
    zip_code: Optional[str] = Field(nullable=True)
    country: Optional[str] = Field(default="Unknown", nullable=True)

    #users: Optional["User"] = Relationship(back_populates="address")
    #pdf_documents: List["PDFDocument"] = Relationship(back_populates="address")