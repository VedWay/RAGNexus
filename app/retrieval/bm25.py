from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self, texts):
        self.texts = texts
        self.tokenized_corpus = [text.split() for text in texts]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query, top_k=3):
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in ranked[:top_k]:
            results.append({
                "text": self.texts[idx],
                "score": score
            })

        return results