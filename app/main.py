from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import shutil
import uuid

from app.api.rag_service import answer_basic_message, answer_question, ingest_and_index


app = FastAPI(title="RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IngestUrlRequest(BaseModel):
    url: str = Field(..., min_length=8)


class AskRequest(BaseModel):
    document_id: str
    question: str = Field(..., min_length=1)
    top_k: int = Field(10, ge=1, le=20)


class BasicChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/ingest/url")
def ingest_url(req: IngestUrlRequest):
    try:
        res = ingest_and_index(req.url)
        return {
            "document_id": res.document_id,
            "source": res.source,
            "raw_count": res.raw_count,
            "chunk_count": res.chunk_count,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    _, ext = os.path.splitext(filename.lower())
    if ext not in {".pdf", ".txt", ".csv"}:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, TXT, or CSV.")

    os.makedirs("storage/uploads", exist_ok=True)
    saved_path = os.path.join("storage", "uploads", f"{uuid.uuid4().hex}{ext}")

    try:
        with open(saved_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.") from e
    finally:
        try:
            file.file.close()
        except Exception:
            pass

    try:
        res = ingest_and_index(saved_path)
        return {
            "document_id": res.document_id,
            "source": res.source,
            "raw_count": res.raw_count,
            "chunk_count": res.chunk_count,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/ask")
def ask(req: AskRequest):
    try:
        return answer_question(document_id=req.document_id, question=req.question, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/chat/basic")
def chat_basic(req: BasicChatRequest):
    try:
        return {"answer": answer_basic_message(req.message), "sources": []}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
