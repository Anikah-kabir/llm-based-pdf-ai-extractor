import re
from typing import List, Dict
from app.core.config import get_settings
from langchain.text_splitter import RecursiveCharacterTextSplitter

settings = get_settings()

def split_text_into_chunks(pages: List[Dict]) -> List[Dict]:
    """Simple fixed-size character chunking with page attribution."""
    CHUNK = settings.max_chunk_chars
    OVER  = settings.max_overlaps

    chunks: List[Dict] = []
    for page in pages:
        t = page["text"]
        i = 0
        while i < len(t):
            chunk = t[i:i+CHUNK]
            chunks.append({"text": chunk, "page_no": page["page_no"]})
            i += max(CHUNK - OVER, 1)
    return chunks

def smart_chunk_text(text: str, page_start: int = 1) -> List[Dict]:
    """Enhanced chunking that preserves tables and maintains context"""
    
    # First identify and protect table structures
    table_pattern = re.compile(
        r'(\+[-]+\+[^\n]*\n)([^\n]*\|[^\n]*\n)+(\+[-]+\+)',
        re.MULTILINE
    )
    
    # Split text into tables and non-table segments
    segments = []
    last_end = 0
    for match in table_pattern.finditer(text):
        # Add text before table
        if match.start() > last_end:
            segments.append({
                'type': 'text',
                'content': text[last_end:match.start()],
                'page': page_start
            })
        
        # Add table
        segments.append({
            'type': 'table',
            'content': match.group(0),
            'page': page_start
        })
        last_end = match.end()
    
    # Add remaining text after last table
    if last_end < len(text):
        segments.append({
            'type': 'text',
            'content': text[last_end:],
            'page': page_start
        })

    # Process each segment appropriately
    chunks = []
    chunk_counter = 1
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.max_chunk_chars,
        chunk_overlap=settings.max_overlaps,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    for segment in segments:
        if segment['type'] == 'table':
            # Handle tables - keep each row as a chunk
            table_rows = segment['content'].split('\n')
            for row in table_rows:
                if row.strip():  # Skip empty rows
                    chunks.append({
                        "content": row,
                        "chunk_num": chunk_counter,
                        "approx_page": segment['page'],
                        "char_count": len(row),
                        "word_count": len(row.split()),
                        "token_estimate": len(row) // 4,
                        "has_tables": True,
                        "has_figures": False,
                        "is_table_row": True
                    })
                    chunk_counter += 1
        else:
            # Process regular text with semantic splitting
            for chunk in splitter.split_text(segment['content']):
                chunks.append({
                    "content": chunk,
                    "chunk_num": chunk_counter,
                    "approx_page": segment['page'],
                    "char_count": len(chunk),
                    "word_count": len(chunk.split()),
                    "token_estimate": len(chunk) // 4,
                    "has_tables": False,
                    "has_figures": "Figure" in chunk[:100],
                    "is_table_row": False
                })
                chunk_counter += 1

    # Calculate accurate page numbers based on content density
    total_chars = sum(len(chunk['content']) for chunk in chunks)
    chars_per_page = total_chars / (page_start + len(chunks)/10)  # Adjust as needed
    
    current_page = page_start
    current_page_chars = 0
    for chunk in chunks:
        current_page_chars += len(chunk['content'])
        if current_page_chars > chars_per_page:
            current_page += 1
            current_page_chars = 0
        chunk['approx_page'] = current_page

    return chunks