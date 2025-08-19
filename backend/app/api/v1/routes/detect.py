from fastapi import APIRouter
from pydantic import BaseModel
from app.services.doc_type_detector import detect_doc_type

router = APIRouter()

class DetectRequest(BaseModel):
    text: str

@router.post("/detect/doc-type")
def detect(req: DetectRequest):
    doc_type, reason = detect_doc_type(req.text)
    return {"doc_type": doc_type, "reason": reason}
