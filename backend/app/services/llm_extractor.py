import openai
from app.core.config import get_settings
from typing import Optional
from pydantic import BaseModel

settings = get_settings()
openai.api_key = settings.openai_api_key

class PromptRequest(BaseModel):
    text: str
    goal: Optional[str] = None
    doc_type: Optional[str] = None  # "medical", "invoice", "resume", etc.


def detect_goal_from_text(text: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Infer the document's goal in one sentence."},
            {"role": "user", "content": text}
        ],
        temperature=0.2
    )
    return response['choices'][0]['message']['content'].strip()


def rule_based_goal_detection(text: str) -> str:
    text_lower = text.lower()
    if "invoice number" in text_lower or "total amount" in text_lower:
        return "Extract invoice information"
    elif "patient name" in text_lower or "diagnosis" in text_lower:
        return "Extract medical data"
    elif "work experience" in text_lower or "skills" in text_lower:
        return "Extract resume details"
    else:
        return "Extract structured data from document"
    
def build_prompt(text: str, goal: Optional[str] = None, doc_type: str = "default") -> str:
    instructions = {
        "medical": "You are a medical document assistant. Extract patient info, diagnosis, treatment, and date fields.",
        "invoice": "You are an invoice parser. Extract invoice number, date, total, tax, and itemized list.",
        "resume": "You are an HR assistant. Extract name, contact, education, work experience, and skills.",
        "default": "You are a document analysis assistant. Your job is to extract structured data from the following text."
    }

    instruction = instructions.get(doc_type or "default", instructions["default"])

    return f"""
        {instruction}

        {f"Goal: {goal}" if goal else ""}

        Text:
        {text}

        Return the data in JSON format.
        """.strip()

def generate_llm_response(prompt: str, model: str = "gpt-4") -> str:
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful PDF document extraction assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response['choices'][0]['message']['content']

def extract_structured_data_from_pdf_text(text: str, goal: Optional[str], doc_type: str = "default") -> dict:
    prompt = build_prompt(text=text, goal=goal, doc_type=doc_type)
    llm_model = "gpt-4"
    response = generate_llm_response(prompt, model=llm_model)
    return {
        "structured_data": response,
        "prompt_used": prompt,
        "llm_used": llm_model
    }
   