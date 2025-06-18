# app/api/deps/db.py

from app.db.session import get_session

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()
