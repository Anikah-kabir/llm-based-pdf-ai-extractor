# app/main.py
from fastapi import FastAPI
from app.api.api_router import api_router
from app.db.session import init_llm_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LLM PDF Extractor")

#import sys
#import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

app = FastAPI(title="LLM PDF Extractor")

# Run DB initialization on startup
@app.on_event("startup")
def on_startup():
    init_llm_db()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # or ["*"] to allow all origins (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],             # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],             # allow all headers
)

# Register all routers
app.include_router(api_router, prefix="/api/v1")