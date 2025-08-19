import fitz
from typing import List, Dict

def extract_text_from_pdf(content: bytes) -> List[Dict]:
    """Return list of {page_no, text} so we retain page info."""
    pages = []
    with fitz.open("pdf", content) as doc:
        for i, page in enumerate(doc):
            pages.append({"page_no": i+1, "text": page.get_text() or ""})
    return pages

def extract_full_text(content: bytes) -> str:
    """Extract all text from PDF concatenated into a single string"""
    full_text = []
    with fitz.open("pdf", content) as doc:
        for page in doc:
            full_text.append(page.get_text() or "")
    return "\n".join(full_text)