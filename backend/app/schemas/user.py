from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime
from .address import AddressRead

class UserBase(SQLModel):
    full_name: Optional[str] = None
    username: str
    email: str
    phone: Optional[str] = None
    age: Optional[datetime] = None
    disabled: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[datetime] = None
    disabled: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    addresses: List[AddressRead] = []
