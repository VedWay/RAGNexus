from fastembed import TextEmbedding
from typing import List
import numpy as np


class Embedder:

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model = TextEmbedding(model_name=model_name)

    def embed_texts(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:

        embeddings = list(self.model.embed(
            texts,
            batch_size=batch_size
        ))

        return self._normalize(np.array(embeddings))

    def _normalize(self, vectors):

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return (vectors / norms).tolist()