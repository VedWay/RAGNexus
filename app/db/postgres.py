import os
import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from dotenv import load_dotenv
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


load_dotenv()


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    chunks: Mapped[List["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    document: Mapped[Document] = relationship(back_populates="chunks")


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if not url:
        raise RuntimeError("DATABASE_URL (or SUPABASE_DB_URL) is not set")
    return url


def get_engine():
    return create_engine(_get_database_url(), pool_pre_ping=True)


SessionLocal = sessionmaker(bind=get_engine(), class_=Session, autoflush=False, autocommit=False)


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


class PostgresStore:
    def __init__(self):
        init_db()

    def session(self) -> Session:
        return SessionLocal()

    def get_or_create_document(self, *, source: str, title: Optional[str] = None, content_hash: Optional[str] = None) -> Document:
        with self.session() as s:
            existing = s.execute(select(Document).where(Document.source == source).limit(1)).scalar_one_or_none()
            if existing:
                return existing

            doc = Document(source=source, title=title, content_hash=content_hash)
            s.add(doc)
            s.commit()
            s.refresh(doc)
            return doc

    def replace_chunks(self, *, document_id: uuid.UUID, chunks: List[Dict[str, Any]]) -> List[Chunk]:
        with self.session() as s:
            s.query(Chunk).filter(Chunk.document_id == document_id).delete()
            rows: List[Chunk] = []
            for c in chunks:
                row = Chunk(
                    document_id=document_id,
                    chunk_index=int(c["chunk_index"]),
                    page_number=c.get("page_number"),
                    text=c["text"],
                    meta=c.get("metadata", {}),
                )
                s.add(row)
                rows.append(row)
            s.commit()
            for r in rows:
                s.refresh(r)
            return rows

    def fetch_chunks_by_ids(self, chunk_ids: Iterable[str]) -> List[Chunk]:
        ids = [uuid.UUID(x) for x in chunk_ids]
        if not ids:
            return []
        with self.session() as s:
            return list(s.execute(select(Chunk).where(Chunk.id.in_(ids))).scalars().all())

    def fetch_all_chunk_texts(self, *, document_id: uuid.UUID) -> List[str]:
        with self.session() as s:
            rows = s.execute(
                select(Chunk.text).where(Chunk.document_id == document_id).order_by(Chunk.chunk_index.asc())
            ).all()
            return [r[0] for r in rows]

    def fetch_all_chunks(self, *, document_id: uuid.UUID) -> List[Chunk]:
        with self.session() as s:
            return list(
                s.execute(
                    select(Chunk).where(Chunk.document_id == document_id).order_by(Chunk.chunk_index.asc())
                )
                .scalars()
                .all()
            )
