from app.embeddings.embedder import Embedder
from app.vectorstore.qdrant_store import QdrantStore
from app.retrieval.hyde import HyDEExpander
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.reranker import Reranker
from app.generation.generator import Generator


def query_rag(query: str):
    # =========================
    # SETUP (same as embed.py)
    # =========================
    embedder = Embedder()
    store = QdrantStore()

    # ⚠️ Load texts again (important for BM25)
    # You may store this globally later (optimization)
    from app.ingestion.pipeline import IngestionPipeline
    pipeline = IngestionPipeline()
    docs = pipeline.ingest("data/sample.pdf")
    texts = [doc.page_content for doc in docs]

    bm25 = BM25Retriever(texts)
    hybrid = HybridRetriever(store, bm25, embedder)
    reranker = Reranker()
    generator = Generator()

    # =========================
    # HYDE
    # =========================
    hyde = HyDEExpander()
    expanded_query = hyde.expand(query)

    # =========================
    # SEARCH
    # =========================
    results = hybrid.search(expanded_query)

    # =========================
    # RERANK
    # =========================
    reranked = reranker.rerank(query, results)

    filtered = reranked[:5]

    # =========================
    # CONTEXTS
    # =========================
    contexts = [r["text"] for r in filtered[:5]]

    # =========================
    # GENERATE
    # =========================
    answer = generator.generate(query, contexts)

    return {
        "answer": answer,
        "contexts": contexts   # 🔥 REQUIRED FOR RAGAs
    }