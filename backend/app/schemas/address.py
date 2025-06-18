from typing import Optional
from sqlmodel import SQLModel

class AddressBase(SQLModel):
    name: Optional[str] = None  # e.g., "Home", "Office"
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = "Unknown"

class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    pass

class AddressRead(AddressBase):
    id: int
    user_id: Optional[int]
