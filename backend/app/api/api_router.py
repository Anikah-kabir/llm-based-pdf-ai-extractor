# app/api/api_router.py

from app.api.v1.routes import pdf_documents
from fastapi import APIRouter
from app.api.v1.routes import auth, users

# API versioned router
api_router = APIRouter()

# Mount different route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(pdf_documents.router, prefix="/pdfs", tags=["PDF Documents"])
