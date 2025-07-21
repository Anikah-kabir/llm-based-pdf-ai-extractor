import fitz  # PyMuPDF

def extract_text_from_pdf(content: bytes) -> str:
    with fitz.open("pdf", content) as doc:
        return "\n".join([page.get_text() for page in doc])