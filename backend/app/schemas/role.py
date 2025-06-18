from pydantic import BaseModel
from typing import Optional
from enum import Enum

class RoleName(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    USER = "user"

class RoleBase(BaseModel):
    name: RoleName
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[RoleName] = None
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: int

    class Config:
        orm_mode = True
