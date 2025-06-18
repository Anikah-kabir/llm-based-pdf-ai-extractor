from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
import sqlalchemy as sa

if TYPE_CHECKING:
    from app.models import UserRoleLink

# Enum for role names
class RoleName(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    USER = "user"

# Shared base for common fields
class RoleBase(SQLModel):
    name: RoleName = Field(sa_column=sa.Column(sa.String, index=True, unique = True, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=sa.Column(sa.String, nullable=True))

# Database model
class Role(RoleBase, table=True):
    __tablename__ = "roles"

    id: int= Field(default=None, primary_key=True)
    user_links: List["UserRoleLink"] = Relationship(back_populates="roles")
