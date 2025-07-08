from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime
from sqlalchemy import event
import uuid
from sqlalchemy.orm import Mapped
import sqlalchemy as sa
#from enum import Enum

# class UserRoleLink(SQLModel, table=True):
#     user_id: uuid.UUID | None = Field(foreign_key="user.id", primary_key=True)
#     role_id: int | None = Field(foreign_key="role.id", primary_key=True) 

# # Enum for role names
# class RoleName(str, Enum):
#     ADMIN = "admin"
#     EDITOR = "editor"
#     VIEWER = "viewer"
#     USER = "user"

# # Shared base for common fields
# class RoleBase(SQLModel):
#     name: RoleName = Field(sa_column=sa.Column(sa.String, index=True, unique = True, nullable=False))
#     description: Optional[str] = Field(default=None, sa_column=sa.Column(sa.String, nullable=True))

# # Database model
# class Role(RoleBase, table=True):
#     id: int= Field(default=None, primary_key=True)
#     users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)

class UserBase(SQLModel):
    full_name: Optional[str] = Field(nullable=False)
    username: str = Field(unique=True, index=True, nullable=False)
    email: EmailStr
    phone: Optional[str] = Field(index=True, nullable=False)
    birthdate: Optional[datetime] = Field(default=None, nullable=True)
    disabled: bool = Field(default=False)
    
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # One-to-many relationship
    #address_id: int | None = Field(default=None,foreign_key="address.id")
    #address: Address | None = Relationship(back_populates="users")

    # Many-to-many with Role
    #roles: list["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)

class UserPublic(UserBase):
    id: uuid.UUID

class UserCreate(SQLModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    phone: Optional[str] = None
    birthdate: Optional[datetime] = None
    
@event.listens_for(User, 'before_update')
def update_timestamps(mapper, connection, target):
    target.updated_at = datetime.utcnow()


#from .user_role import UserRoleLink  # avoid circular ref
#User.roles = Relationship(back_populates="users", link_model=UserRoleLink)