from app.core.config import get_settings
from sqlmodel import SQLModel, create_engine
from typing import Generator

settings = get_settings()

def get_engine(db_url: str):
    return create_engine(db_url, echo=True)

def init_db(engine):
    SQLModel.metadata.create_all(engine)

engine = get_engine(settings.database_url)

def init_llm_db():
    init_db(engine)