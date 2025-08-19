# app/services/doc_type.py
from app.core.config import get_settings
from openai import OpenAI

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

def detect_doc_type_rule_based(text: str) -> str:
    tl = text.lower()
    medical = ["patient", "diagnosis", "treatment", "blood pressure", "prescription", "clinical"]
    invoice = ["invoice number", "total", "subtotal", "tax", "bill to", "quantity", "unit price"]
    resume  = ["education", "work experience", "skills", "summary", "objective", "linkedin"]

    if any(k in tl for k in medical):
        return "medical"
    if any(k in tl for k in invoice):
        return "invoice"
    if any(k in tl for k in resume):
        return "resume"
    return "default"

def detect_doc_type_llm(sample_text: str) -> str:
    if not client:
        return "default"
    prompt = f"""Classify this document as one word: medical, invoice, resume, default.
Only return the word.

Text (truncated):
{sample_text[:1200]}"""
    try:
        r = client.chat.completions.create(
            model=settings.chat_model,
            messages=[{"role":"user","content": prompt}],
            temperature=0.0
        )
        return r.choices[0].message.content.strip().lower()
    except Exception:
        return "default"

def auto_detect_doc_type(pages: list[dict]) -> str:
    # concatenate first N pages for signal
    joined = "\n".join([p["text"] for p in pages[:3]])[:3000]
    rb = detect_doc_type_rule_based(joined)
    return rb if rb != "default" else detect_doc_type_llm(joined)
