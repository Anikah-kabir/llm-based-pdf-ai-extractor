from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserRoleAssign(BaseModel):
    user_id: int
    role_id: int
    assigned_by: Optional[str] = None

class UserRoleResponse(BaseModel):
    user_id: int
    role_id: int
    assigned_by: Optional[str] = None
    assigned_at: datetime

    class Config:
        orm_mode = True
