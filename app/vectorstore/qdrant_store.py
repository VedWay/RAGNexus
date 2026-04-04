from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

class QdrantStore:
    def __init__(self):
        self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = "documents"

    def create_collection(self):
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=384,  # embedding dimension
                distance=Distance.COSINE
            )
        )

    def upload(self, vectors, texts):
        points = []

        for i, (vec, text) in enumerate(zip(vectors, texts)):
            points.append({
                "id": i,
                "vector": vec,
                "payload": {"text": text}
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