from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Response, Request, Body, Form
from jose import JWTError, jwt
from sqlmodel import Session, select
from app.models import User, UserPublic, UserCreate
from app.api.deps.auth import get_current_user, create_access_token, get_password_hash, verify_password
from app.api.deps.db import get_session
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime
import uuid
from app.core.config import get_settings

settings = get_settings()
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/me", response_model=UserPublic)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/register", response_model=UserPublic)
def register_user( 
        user_data: UserCreate = Body(...), 
        db:Session = Depends(get_session)
    ):
    #print(f"Received: {user_data.username}, {user_data.email}, {user_data.full_name}, {user_data.birthdate}")
    # Check if username or email already exists
    if db.exec(select(User).where(User.username == user_data.username)).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.exec(select(User).where(User.email == user_data.email)).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        phone=user_data.phone,
        birthdate=user_data.birthdate,
        disabled=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/refresh-token")
def refresh_token(response: Response, request: Request, db: Session = Depends(get_session)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(refresh_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Issue new access token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
