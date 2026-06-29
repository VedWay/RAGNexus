from fastembed.rerank.cross_encoder import TextCrossEncoder

class Reranker:
    def __init__(self):
        self.model = TextCrossEncoder(model_name="Xenova/ms-marco-MiniLM-L-6-v2")

    def rerank(self, query, docs):
        texts = [doc["text"] for doc in docs]
        scores = list(self.model.rerank(query, texts))

        for i in range(len(docs)):
            docs[i]["rerank_score"] = scores[i]

        docs = sorted(docs, key=lambda x: x["rerank_score"], reverse=True)
        return docs