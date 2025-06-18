# app/schemas/tag.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class TagCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class TagResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    class Config:
        orm_mode = True
