from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class Embedder:

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True
        )

        return self._normalize(embeddings)

    def _normalize(self, vectors):

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return (vectors / norms).tolist()