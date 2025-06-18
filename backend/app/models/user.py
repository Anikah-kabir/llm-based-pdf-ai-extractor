from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import event, Column, String, Integer, Date
import uuid

if TYPE_CHECKING:
    from app.models import Address, UserRoleLink

class UserBase(SQLModel):
    full_name: Optional[str] = Field(sa_column=Column(String, nullable=False))
    username: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    email: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    phone: Optional[str] = Field(default=None, sa_column=Column(String, index=True, nullable=False))
    birthdate: Optional[datetime] = Field(default=None, sa_column=Column(Date, nullable=True))
    disabled: bool = False

class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(sa_column=Column(String, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # One-to-many relationship
    addresses: List["Address"] = Relationship(back_populates="users")

    # Many-to-many with Role
    role_links: list["UserRoleLink"] = Relationship(back_populates="users")


@event.listens_for(User, 'before_update')
def update_timestamps(mapper, connection, target):
    target.updated_at = datetime.utcnow()