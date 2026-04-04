import os

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

class QdrantStore:
    def __init__(self):
        url = os.getenv("QDRANT_URL")
        if url:
            self.client = QdrantClient(url=url)
        else:
            host = os.getenv("QDRANT_HOST", "localhost")
            port = int(os.getenv("QDRANT_PORT", "6333"))
            self.client = QdrantClient(host=host, port=port)
        self.collection_name = "documents"

    def create_collection(self):
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=384,  # embedding dimension
                distance=Distance.COSINE
            )
        )

    def upload(self, vectors, payloads=None, ids=None, texts=None):
        points = []

        if payloads is None:
            payloads = []
            if texts is None:
                texts = []
            for text in texts:
                payloads.append({"text": text})

        if ids is None:
            ids = list(range(len(vectors)))

        for point_id, vec, payload in zip(ids, vectors, payloads):
            points.append({
                "id": point_id,
                "vector": vec,
                "payload": payload
            })

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_vector, top_k=3):
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        ).points

        return results