from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
import sqlalchemy as sa
import uuid

if TYPE_CHECKING:
    from app.models import User, PDFDocument

class Address(SQLModel, table=True):
    __tablename__ = "addresses"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, foreign_key="user.id")
    name: Optional[str] = Field(sa_column=sa.Column(sa.String, nullable=True))  # Optional: "Home", "Work", etc.
    street: Optional[str] = Field(sa_column=sa.Column(sa.String, nullable=True)) 
    city: Optional[str] = Field(sa_column=sa.Column(sa.String, nullable=True)) 
    state: Optional[str] = Field(sa_column=sa.Column(sa.String, nullable=True)) 
    zip_code: Optional[str] = Field(sa_column=sa.Column(sa.String, nullable=True)) 
    country: Optional[str] = Field(default="Unknown", sa_column=sa.Column(sa.String, nullable=True))

    user: Optional["User"] = Relationship(back_populates="addresses")
    pdf_documents: List["PDFDocument"] = Relationship(back_populates="addresses")