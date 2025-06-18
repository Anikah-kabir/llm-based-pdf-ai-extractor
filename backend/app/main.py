# app/main.py
from fastapi import FastAPI
from app.api.api_router import api_router
from app.db.session import init_llm_db

app = FastAPI(title="LLM PDF Extractor")

#import sys
#import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

app = FastAPI(title="LLM PDF Extractor")

# Run DB initialization on startup
@app.on_event("startup")
def on_startup():
    init_llm_db()

# Register all routers
app.include_router(api_router)

