from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.llm_extractor import build_prompt, generate_llm_response

router = APIRouter()

class PromptRequest(BaseModel):
    text: str
    goal: Optional[str] = None
    doc_type: Optional[str] = None  # "medical", "invoice", "resume", etc.

@router.post("/engineer")
def engineer_prompt(req: PromptRequest):
    prompt = build_prompt(req.text, req.goal, req.doc_type)
    response = generate_llm_response(prompt)
    return {
        "prompt": prompt,
        "response": response
    }
