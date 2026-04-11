# RAGNexus - Hybrid RAG API + Web Chat

Full-stack Retrieval-Augmented Generation project with:
- FastAPI backend for ingestion and Q&A
- React (Vite) frontend for chat UI
- Hybrid retrieval (vector + BM25) with HyDE query expansion
- Cross-encoder reranking
- Optional RAGAs evaluation

## What is implemented

- Ingest from URL, PDF, TXT, and CSV
- Store document/chunk metadata in PostgreSQL
- Store embeddings in Qdrant
- Query pipeline:
  HyDE expansion -> hybrid retrieval -> rerank -> grounded answer generation
- Basic non-document chat mode using Groq
- Frontend chat workspace with source citations

## Architecture

Document flow:

Source (URL/file) -> Loader -> Chunker -> Embeddings
-> PostgreSQL (documents/chunks) + Qdrant (vectors)

Question flow (document mode):

Question -> HyDE -> Hybrid Retriever (Qdrant + BM25)
-> Cross-Encoder Reranker -> Top contexts -> Groq LLM -> Answer + Sources

## Tech stack

- Backend: FastAPI, SQLAlchemy
- Vector DB: Qdrant
- Relational DB: PostgreSQL (Supabase Postgres also supported)
- Retrieval: BM25 + dense vector search + HyDE + reranker
- LLM: Groq (llama-3.1-8b-instant)
- Frontend: React + Vite

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL database
- Qdrant server
- Groq API key

## Setup

### 1) Python dependencies

From project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Frontend dependencies

```bash
cd web
npm install
cd ..
```

### 3) Environment variables

Create a .env file in the project root:

```env
# Required for generation/HyDE/basic chat
GROQ_API_KEY=your_groq_api_key

# Required by app/db/postgres.py
# Use either DATABASE_URL or SUPABASE_DB_URL
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/rag
# SUPABASE_DB_URL=postgresql+psycopg2://...

# Qdrant options (use one style)
QDRANT_URL=http://localhost:6333
# or:
# QDRANT_HOST=localhost
# QDRANT_PORT=6334
```

Notes:
- If you run Qdrant with Docker default port mapping (6333), set QDRANT_URL to http://localhost:6333.
- If QDRANT_URL is not set, backend falls back to QDRANT_HOST/QDRANT_PORT.

### 4) Run Qdrant (Docker)

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 5) Run backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6) Run frontend

```bash
cd web
npm run dev
```

Open the app at http://localhost:5173

## API endpoints

- GET /health
- POST /ingest/url
- POST /ingest/file
- POST /ask
- POST /chat/basic

Example calls:

```bash
curl -X GET http://localhost:8000/health
```

```bash
curl -X POST http://localhost:8000/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"document_id":"YOUR_DOCUMENT_ID","question":"What is this about?","top_k":10}'
```

## Evaluation (optional)

Run RAGAs evaluation:

```bash
python -m app.evaluation.evaluate
```

Default metrics used:
- faithfulness
- answer_relevancy
- context_recall

## Project structure

```text
rag/
  app/
    api/            # API service orchestration
    db/             # PostgreSQL models/store, Qdrant client
    embeddings/     # Sentence-transformers embedder
    evaluation/     # RAGAs dataset and evaluator
    generation/     # Groq generator
    ingestion/      # URL/PDF/TXT/CSV loader + chunking pipeline
    retrieval/      # BM25, hybrid, HyDE, reranker
    vectorstore/    # Qdrant store wrapper
    main.py         # FastAPI app
  web/              # React + Vite frontend
  scripts/          # Local utility scripts
  data/             # Input data
  storage/uploads/  # Uploaded files
```

## Current behavior notes

- /ingest/file accepts only PDF, TXT, CSV.
- /ask requires a valid document_id returned by an ingest endpoint.
- In document mode, answers are constrained by retrieved context and returned with sources.
- Basic chat mode does not use document retrieval.

## Troubleshooting

- Database URL error:
  Set DATABASE_URL or SUPABASE_DB_URL in .env.
- Qdrant connection error:
  Ensure Qdrant is running and URL/host/port match your config.
- CORS/proxy issues in web:
  Ensure backend is running on port 8000 and frontend on 5173.