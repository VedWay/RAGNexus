# RAG Pipeline with Hybrid Retrieval & RAGAs Evaluation

A production-ready Retrieval-Augmented Generation (RAG) system with advanced retrieval techniques and comprehensive evaluation.

## Features

- **Document Ingestion**: PDF loading with intelligent chunking
- **Hybrid Retrieval**: Combines vector search (Qdrant) + BM25 for better recall
- **HyDE (Hypothetical Document Embeddings)**: Query expansion for improved retrieval
- **Cross-Encoder Reranking**: Reorders results for better relevance
- **LLM Generation**: Uses Groq's Llama 3.1 for fast, free inference
- **RAGAs Evaluation**: Automated metrics (faithfulness, answer relevancy, context recall)

## Architecture

```
Query → HyDE Expansion → Hybrid Search (Vector + BM25) 
  → Reranker → Top-K Contexts → LLM → Answer
```

### Components

| Module | Purpose |
|--------|---------|
| `app/ingestion/` | PDF loading, text chunking |
| `app/embeddings/` | Sentence-transformers embeddings |
| `app/vectorstore/` | Qdrant vector database |
| `app/retrieval/` | BM25, hybrid search, HyDE, reranker |
| `app/generation/` | Groq LLM integration |
| `app/evaluation/` | RAGAs evaluation pipeline |

## Setup

### 1. Install Dependencies

```bash
pip install langchain langchain-community langchain-groq langchain-huggingface
pip install qdrant-client sentence-transformers rank-bm25 ragas datasets
pip install pypdf groq python-dotenv
```

### 2. Configure Environment

Create `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key at [groq.com](https://groq.com)

### 3. Start Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

## Usage

### Ingest Documents

```bash
python3 scripts/ingest.py
```

This processes PDFs in `data/` and stores embeddings in Qdrant.

### Query the RAG System

```python
from app.retrieval.pipeline import query_rag

result = query_rag("What is GDB?")
print(result["answer"])
print(result["contexts"])  # Retrieved chunks
```

### Run Evaluation

```bash
python3 -m app.evaluation.evaluate
```

Evaluates using RAGAs metrics with free HuggingFace embeddings and Groq LLM.

## Project Structure

```
rag/
├── app/
│   ├── core/              # Config, logging
│   ├── db/                # Postgres, Qdrant clients
│   ├── embeddings/        # Embedding models
│   ├── evaluation/        # RAGAs evaluation
│   ├── generation/        # LLM generation
│   ├── ingestion/         # Document processing
│   ├── retrieval/         # Search, reranking, HyDE
│   └── vectorstore/       # Qdrant store
├── data/                  # Input PDFs
├── scripts/               # CLI utilities
└── storage/               # Local storage
```

## Key Files

- `app/retrieval/pipeline.py` - Main RAG pipeline
- `app/evaluation/evaluate.py` - RAGAs evaluation
- `scripts/embed.py` - Generate embeddings
- `scripts/query.py` - CLI query tool

## Evaluation Metrics

- **Faithfulness**: Is the answer grounded in the retrieved contexts?
- **Answer Relevancy**: Is the answer relevant to the question?
- **Context Recall**: Did we retrieve all relevant context?
