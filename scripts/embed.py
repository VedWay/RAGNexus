import sys
import os

# Fix import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ingestion.pipeline import IngestionPipeline
from app.embeddings.embedder import Embedder
from app.vectorstore.qdrant_store import QdrantStore

from app.retrieval.hyde import HyDEExpander
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.reranker import Reranker

from app.generation.generator import Generator


# =========================
# STEP 1: INGEST DOCUMENT
# =========================
pipeline = IngestionPipeline()
docs = pipeline.ingest("data/sample.pdf")

texts = [doc.page_content for doc in docs]

print(f"📄 Raw pages: {len(docs)}")


# =========================
# STEP 2: EMBEDDINGS
# =========================
embedder = Embedder()
vectors = embedder.embed_texts(texts)

print(f"🔢 Total chunks: {len(vectors)}")
print(f"📐 Embedding dim: {len(vectors[0])}")

for chunk in texts:
    if "GDB" in chunk or "gdb" in chunk:
        print("✅ FOUND GDB CHUNK:\n", chunk)

# =========================
# STEP 3: STORE IN QDRANT
# =========================
store = QdrantStore()
store.create_collection()
store.upload(vectors, texts)

print("✅ Stored in Qdrant!")


# =========================
# STEP 4: BM25 + HYBRID
# =========================
bm25 = BM25Retriever(texts)
hybrid = HybridRetriever(store, bm25, embedder)


# =========================
# STEP 5: RERANKER
# =========================
reranker = Reranker()


# =========================
# STEP 6: QUERY
# =========================
query = "What are proxy settings ?"

print(f"\n🔍 Query: {query}")

# =========================
# STEP 7: HYDE EXPANSION
# =========================
hyde = HyDEExpander()
expanded_query = hyde.expand(query)

print(f"\n🧠 Expanded Query: {expanded_query}")


# =========================
# STEP 8: HYBRID SEARCH
# =========================
results = hybrid.search(expanded_query)

print("\n🔥 Hybrid Results (Before Rerank):\n")

for i, res in enumerate(results[:5]):
    print(f"Result {i+1} | Score: {res['score']}")
    print(res["text"][:200])
    print("------")


# =========================
# STEP 9: RERANKING
# =========================
reranked_results = reranker.rerank(expanded_query, results)

# ✅ FILTER ONLY RELEVANT RESULTS
filtered_results = reranked_results[:5]

print("\n🎯 Final Filtered Results:\n")

for i, res in enumerate(filtered_results):
    print(f"Result {i+1} | Score: {res['rerank_score']}")
    print(res["text"][:200])
    print("------")

# =========================
# STEP 10: GENERATE ANSWER
# =========================

generator = Generator()

contexts = [res["text"] for res in filtered_results]

answer = generator.generate(query, contexts)

print("\n🧠 FINAL ANSWER:\n")
print(answer)