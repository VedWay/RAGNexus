from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self):
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank(self, query, docs):
        pairs = [(query, doc["text"]) for doc in docs]
        scores = self.model.predict(pairs)

        for i in range(len(docs)):
            docs[i]["rerank_score"] = scores[i]

        docs = sorted(docs, key=lambda x: x["rerank_score"], reverse=True)
        return docs