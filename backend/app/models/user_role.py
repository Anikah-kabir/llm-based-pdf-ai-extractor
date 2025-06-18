from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
import sqlalchemy as sa

if TYPE_CHECKING:
    from app.models import User, Role

class UserRoleLink(SQLModel, table=True):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)
    
    assigned_by_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, foreign_key="user.id")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="role_links")
    role: Optional["Role"] = Relationship(back_populates="user_links")

#if TYPE_CHECKING:
    