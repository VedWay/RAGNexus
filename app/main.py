from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import shutil
import uuid

from app.auth.security import (
    ACCESS_TOKEN_MINUTES,
    REFRESH_TOKEN_DAYS,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.api.rag_service import answer_basic_message, answer_question, ingest_and_index
from app.db.postgres import PostgresStore, User


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


class AuthRegisterRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)
    full_name: str | None = Field(default=None, min_length=1)


class AuthLoginRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)


class AuthRefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


def _token_payload(user: User):
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
        },
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
        "token_type": "bearer",
        "access_expires_in": ACCESS_TOKEN_MINUTES * 60,
        "refresh_expires_in": REFRESH_TOKEN_DAYS * 24 * 60 * 60,
    }


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/auth/register")
def register(req: AuthRegisterRequest):
    pg = PostgresStore()
    email = req.email.strip().lower()
    existing = pg.get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=409, detail="Email is already registered")

    user = pg.create_user(
        email=email,
        password_hash=hash_password(req.password),
        full_name=req.full_name.strip() if req.full_name else None,
    )
    return _token_payload(user)


@app.post("/auth/login")
def login(req: AuthLoginRequest):
    pg = PostgresStore()
    user = pg.get_user_by_email(req.email.strip().lower())
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _token_payload(user)


@app.post("/auth/refresh")
def refresh(req: AuthRefreshRequest):
    payload = decode_token(req.refresh_token)
    if payload.get("token_type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    pg = PostgresStore()
    user = pg.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return _token_payload(user)


@app.post("/ingest/url")
def ingest_url(req: IngestUrlRequest, _: User = Depends(get_current_user)):
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
async def ingest_file(file: UploadFile = File(...), _: User = Depends(get_current_user)):
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
def ask(req: AskRequest, _: User = Depends(get_current_user)):
    try:
        return answer_question(document_id=req.document_id, question=req.question, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/chat/basic")
def chat_basic(req: BasicChatRequest, _: User = Depends(get_current_user)):
    try:
        return {"answer": answer_basic_message(req.message), "sources": []}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
