# 🧠 PDF Extraction & RAG Chat System
This project provides an **end-to-end system** for:
- Uploading PDFs and extracting structured data using **LLM Prompt Engineering**
- Automatic **document type & goal detection**
- Storing document chunks in **Weaviate vector database**
- Querying documents using **RAG (Retrieval-Augmented Generation)**
- Frontend React UI for **PDF Upload**, **Prompt Playground**, and **Chat-based RAG search**

---

## Features

### Backend (FastAPI)
- Upload PDF (`/pdfs/upload`)
- Extract text and structured data
- Auto-detect goal (medical, invoice, resume, general)
- Store PDF data in **PostgreSQL**
- Index document chunks in **Weaviate**
- Query knowledge base using RAG (`/rag/query`)

### Frontend (React)
- **PDF Upload Page** → Upload PDFs, set document type & goal
- **Prompt Playground** → Test prompt engineering interactively
- **RAG Chat Assistant** → Conversational retrieval across uploaded PDFs

---

## Setup Instructions

### 1. Clone Repo

```bash
git clone https://github.com/yourname/llm-pdf-extractor.git
cd llm-pdf-extractor/backend


---

- LLM integration instructions (like with [Ollama](https://ollama.com/))
- Docker setup
- Swagger/OpenAPI customization info
- API test examples (with `httpie` or `curl`)


---
## Database Table Structure

llm_db=# \dt
               List of relations
 Schema |        Name        | Type  |  Owner
--------+--------------------+-------+----------
 public | addresses          | table | llm_user
 public | alembic_version    | table | llm_user
 public | pdf_documents      | table | llm_user
 public | pdfdocumenttaglink | table | llm_user
 public | roles              | table | llm_user
 public | tags               | table | llm_user
 public | userrolelink       | table | llm_user
 public | users              | table | llm_user

## Database pdf_documents table metadata
 llm_db=# \d pdf_documents
                        Table "public.pdf_documents"
     Column     |           Type           | Collation | Nullable | Default
----------------+--------------------------+-----------+----------+---------
 id             | uuid                     |           | not null |
 filename       | character varying        |           | not null |
 upload_time    | timestamp with time zone |           | not null |
 extracted_text | text                     |           |          |
 meta           | text                     |           |          |
 extracted_data | json                     |           |          |
 llm_used       | character varying        |           |          |
 prompt_used    | character varying        |           |          |
 status         | character varying        |           | not null |
 is_public      | boolean                  |           | not null |
 address_id     | integer                  |           |          |
 uploaded_by_id | uuid                     |           |          |
Indexes:
    "pdf_documents_pkey" PRIMARY KEY, btree (id)
    "ix_pdf_documents_id" btree (id)
Referenced by:
    TABLE "pdfdocumenttaglink" CONSTRAINT "pdfdocumenttaglink_pdf_document_id_fkey" FOREIGN KEY (pdf_document_id) REFERENCES pdf_documents(id)
