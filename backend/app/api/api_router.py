from app.api.v1.routes import pdfs
from fastapi import APIRouter
from app.api.v1.routes import auth, users
from app.api.v1.routes import prompts
from app.api.v1.routes import detect
from app.api.v1.routes import chunks
# API versioned router
api_router = APIRouter()

# Mount different route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(pdfs.router, prefix="/pdfs", tags=["PDF Documents"])
api_router.include_router(chunks.router, prefix="/chunks", tags=["Chunks"])
api_router.include_router(prompts.router, prefix="/prompt", tags=["Prompt Engineering"])
api_router.include_router(detect.router, prefix="/detect", tags=["Detection"])
