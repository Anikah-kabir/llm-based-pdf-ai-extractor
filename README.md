# 🧠 LLM PDF Extractor

A microservices-based application to extract **structured data from PDF documents** using **Local Large Language Models (LLMs)**. Built with **FastAPI**, **SQLModel**, and **PostgreSQL**, styled with TailwindCSS.

---

## Features

- Upload PDFs and extract structured data
- Local LLM-based extraction & intelligent tagging (Ollama compatible)
- JWT & Role-based Access Control (RBAC)
- Multi-tenant support
- Many-to-many tagging system (PDFs ↔ Tags)
- REST APIs using FastAPI
- Modular microservices
- TailwindCSS frontend
- Docker support

---
Process Flow:
- User uploads PDF from the frontend.
- FastAPI backend saves metadata and PDF content.
- LLM Engine (Ollama) loads the local model (e.g., mistral:instruct).
- We define a prompt template, such as:
    ```bash
	“Extract invoice number, customer name, and total amount from the following text: ...”

- PDF text is sent to the LLM via a local Ollama API.
- The model returns structured JSON (e.g., { "invoice_number": "1234", "amount": "$540.00" }).
- FastAPI stores this data in the database (JSONB column).
- Frontend displays it in a user-friendly format.

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
