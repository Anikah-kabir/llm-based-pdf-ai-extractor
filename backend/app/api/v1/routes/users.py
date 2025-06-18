from fastapi import APIRouter, Depends
from app.api.deps.auth import get_current_user
from app.models import User

router = APIRouter()

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
