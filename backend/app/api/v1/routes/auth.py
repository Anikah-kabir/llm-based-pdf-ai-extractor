from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.utils.auth import create_access_token, get_password_hash, verify_password
from app.api.deps.db import get_db
from sqlmodel import Session, select

router = APIRouter()

@router.post("/register")
def register(user_data: dict, session: Session = Depends(get_db)):
    user = User(**user_data)
    user.hashed_password = get_password_hash(user_data["password"])
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "email": user.email}

@router.post("/login")
def login(form_data: dict, session: Session = Depends(get_db)):
    statement = select(User).where(User.email == form_data["email"])
    user = session.exec(statement).first()
    if not user or not verify_password(form_data["password"], user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token({"sub": str(user.id)}), "token_type": "bearer"}
