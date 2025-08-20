from __future__ import annotations
from typing import Optional, Tuple
import os
import re
from openai import OpenAI, APIConnectionError, RateLimitError
from app.core.config import get_settings

settings = get_settings()

# --- canonical labels your system uses ---
CANONICAL_TYPES = {"medical", "invoice", "resume", "default"}

if settings.use_ollama:
    client = OpenAI(
        base_url=f"{settings.ollama_api_endpoint}/v1/",
        api_key="ollama"
    )
else:
    client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

# --- quick rules (cheap & fast) ---
def rule_based_doc_type(text: str) -> Tuple[str, str]:
    """
    Return (doc_type, reason). 'reason' is useful to store for audit/debug.
    """
    t = text.lower()

    # medical hints
    if any(k in t for k in [
        "patient id", "hemoglobin", "diagnosis", "prescription", "blood pressure",
        "icd-10", "lab result", "admission date", "patient", "health"
    ]):
        return "medical", "matched medical keywords"

    # invoice hints
    if any(k in t for k in [
        "invoice number", "invoice","subtotal", "total amount", "vat", "net 30", "bill to",
        "purchase order", "po #", "line items"
    ]):
        return "invoice", "matched invoice keywords"

    # resume hints
    if any(k in t for k in [
        "work experience", "profile", "education", "skills", "summary", "linkedin.com/in/",
        "curriculum vitae", "certifications"
    ]):
        return "resume", "matched resume keywords"

    return "default", "no strong match"

# --- LLM fallback (optional) ---
def llm_doc_type(text: str) -> Optional[str]:
    """
    Ask LLM for doc type. Returns one of CANONICAL_TYPES or None if it fails.
    """
    use_llm = settings.doc_type_detect_use_llm
    if not use_llm:
        return None

    model = settings.ollama_model if settings.use_ollama else settings.doc_type_detect_model
    max_chars = settings.doc_type_detect_max_chars

    trimmed = text[:max_chars]

    prompt = f"""
You are a classifier. Given the document text, output ONE WORD from this set exactly:
{", ".join(sorted(CANONICAL_TYPES))}

Choose the best fit:
- medical: clinical notes, lab results, patient info
- invoice: billing docs (invoice number, totals, line items)
- resume: CV, work experience, skills
- default: anything else

Document:
\"\"\"{trimmed}\"\"\"

Answer with only one of: medical | invoice | resume | default
""".strip()

    try:
        # Chat Completions (recommended)
        resp = client.chat.completions.create(
            model=model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": "Return only one label."},
                {"role": "user", "content": prompt}
            ],
        )
        label = resp.choices[0].message.content.strip().lower()
        # normalize
        label = re.sub(r"[^a-z]", "", label)
        if label in CANONICAL_TYPES:
            return label
    except APIConnectionError as e:
        raise
        return "Error: Could not connect to LLM service"
    except RateLimitError:
       raise
    except Exception as e:
        # log if you have logger
        # logger.exception("LLM doc_type detection failed: %s", e)
        raise

    return None

def detect_doc_type(text: str) -> Tuple[str, str]:
    """
    Full detection pipeline:
      - rule-based first
      - LLM only if rule says 'default' or low confidence
    Returns (doc_type, trace_reason)
    """
    rb_type, rb_reason = rule_based_doc_type(text)

    # if rule-based already confident, keep it
    if rb_type != "default":
        return rb_type, f"rule-based: {rb_reason}"

    # try LLM
    llm_type = llm_doc_type(text)
    if llm_type:
        return llm_type, "llm-based"

    # fallback still default
    return "default", "fallback default"
