import fitz  
import pandas as pd
from langchain_core.documents import Document
from typing import List


import fitz
from langchain_core.documents import Document
from typing import List


class DocumentLoader:

    def load_pdf(self, path: str) -> List[Document]:
        docs = []
        try:
            pdf = fitz.open(path)
        except Exception as e:
            raise ValueError(f"Invalid or corrupted PDF: {path}") from e

        for i, page in enumerate(pdf):
            text = page.get_text()
            if text.strip():  # avoid empty pages
                docs.append(
                    Document(
                        page_content=text,
                        metadata={"source": path, "page": i}
                    )
                )
        return docs

    def load_txt(self, path: str) -> List[Document]:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        return [Document(page_content=text, metadata={"source": path})]

    def load_csv(self, path: str) -> List[Document]:
        df = pd.read_csv(path)
        docs = []

        for i, row in df.iterrows():
            content = " | ".join([str(v) for v in row.values])
            docs.append(
                Document(
                    page_content=content,
                    metadata={"source": path, "row": i}
                )
            )
        return docs