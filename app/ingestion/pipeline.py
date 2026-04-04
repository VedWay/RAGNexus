from typing import List
from langchain_core.documents import Document
from app.ingestion.loader import DocumentLoader
from app.ingestion.chunking import Chunker


class IngestionPipeline:

    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = Chunker()

    def ingest(self, path: str) -> List[Document]:
        docs = []

        if path.endswith(".pdf"):
            docs = self.loader.load_pdf(path)

        elif path.endswith(".txt"):
            docs = self.loader.load_txt(path)

        elif path.endswith(".csv"):
            docs = self.loader.load_csv(path)

        else:
            raise ValueError("Unsupported file type")

        # Apply chunking
        chunks = self.chunker.chunk(docs)

        return chunks