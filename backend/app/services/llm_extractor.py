import sys
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from openai import OpenAI
import logging
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import get_settings
import json

logging.basicConfig(
    filename='logs/app.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

settings = get_settings()
if settings.use_ollama:
    client = OpenAI(
        base_url=f"{settings.ollama_host}/v1/",
        api_key="ollama"
    )
else:
    client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

class PromptRequest(BaseModel):
    text: str
    goal: Optional[str] = None
    doc_type: Optional[str] = "default"

def build_prompt(text: str, goal: Optional[str], doc_type: str) -> str:
    instructions = {
        "medical": "Extract patient info (name, id), dates, diagnoses, treatments, meds. Return clean JSON.",
        "invoice": "Extract invoice_number, date, vendor, line_items[], subtotal, tax, total. Return clean JSON.",
        "resume":  "Extract name, contacts, education[], experience[], skills[]. Return clean JSON.",
        "default": "Extract key fields and return clean JSON."
    }
    head = instructions.get(doc_type or "default", instructions["default"])
    return f"""{head}
Goal: {goal or "Extract structured data"}
Text:
{text[:4000]}

Rules:
- Return ONLY JSON (no prose).
- Use snake_case keys.
"""

def generate_llm_response(prompt: str) -> str:
    """
    Generate LLM response.
    
    Args:
        prompt: Input prompt text
        
    Returns:
        str: Generated response or error message
    """
    if not client:
        return '{"status":false, "error": "LLM client not initialized", "note": "Provide OPENAI_API_KEY or enable Ollama"}'
    
    try:
        response = client.chat.completions.create(
            model=settings.ollama_model if settings.use_ollama else settings.chat_model,
            messages=[
                {"role": "system", "content": "You are a careful information extraction assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            stream=False
        )
        return {"status":True, "content": response.choices[0].message.content}
    except APIConnectionError as e:
        logging.error(f"Connection error: {str(e)}")
        return '{"status":false, "error": "Connection failed", "details": "Check your network or LLM service"}'
        
    except RateLimitError as e:
        logging.warning(f"Rate limit exceeded: {str(e)}")
        return '{"status":false, "error": "Rate limit exceeded", "solution": "Wait or check quota"}'
        
    except APIStatusError as e:

        logging.error(f"API error (HTTP {e.status_code}): {e.message}")
        if e.status_code == 401:
            return '{"status":false, "error": "Authentication failed", "action": "Check API keys"}'
        elif e.status_code == 404:
            return '{"status":false, "error": "Model not found", "action": "Verify model name"}'
        else:
            return f'{{"status":false, "error": "API error {e.status_code}", "details": "{e.message}"}}'
            
    except Exception as e:
        logging.exception(f"Unexpected error: {str(e)}")
        return f'{{"status":false, "error": "Processing failed", "details": "{str(e)}"}}'
    

def extract_structured_data_from_text(text: str, goal: Optional[str], doc_type: str) -> Dict[str, Any]:
    prompt = build_prompt(text, goal, doc_type)

    contentResponse = generate_llm_response(prompt)
    if(contentResponse['status'] or contentResponse['status']=='false'):
        return {
            "structured_data": contentResponse['content'],
            "prompt_used": prompt,
            "llm_used": settings.ollama_model if settings.use_ollama else settings.chat_model
        }
    else:
        return contentResponse
    

def synthesize_answer(question: str, contexts: List[str]) -> str:
    ctx = "\n\n".join(contexts)[:6000]
    if not client:
        return f"(LLM disabled) You asked: {question}\nTop contexts:\n{ctx[:800]}"
    prompt = f"""Answer the question using ONLY the context. Be concise. If unknown, say you don't know.

Context:
{ctx}

Question: {question}
Answer:"""
    r = client.chat.completions.create(
        model=settings.ollama_model if settings.use_ollama else settings.chat_model,
        messages=[{"role":"user","content": prompt}],
        temperature=0.1
    )
    return r.choices[0].message.content.strip()

async def process_chunk_with_llm(chunk: Dict, doc_type: str) -> Dict:
    """Enhance chunk with LLM analysis"""
    prompt = f"""
    Analyze this {doc_type} document chunk and extract:
    1. Key entities (people, organizations, dates)
    2. Main topics
    3. Action items (if any)
    
    Chunk Content:
    {chunk['content']}
    
    Return JSON format:
    {{
        "entities": ["list"],
        "topics": ["list"],
        "actions": ["list"],
        "summary": "string"
    }}
    """
    
    response = generate_llm_response(prompt)
    if not response.get("status"):
        logging.error(f"LLM processing failed for chunk {chunk['chunk_num']}")
        return {"llm_error": response.get("error")}
    
    try:
        return {
            **chunk,
            "llm_analysis": json.loads(response["content"]),
            "processed": True
        }
    except json.JSONDecodeError:
        return {
            **chunk,
            "llm_analysis": {"error": "Invalid LLM response format"},
            "processed": False
        }