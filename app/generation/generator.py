from dotenv import load_dotenv

load_dotenv()

from groq import Groq
import os

class Generator:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate(self, query, contexts):
        context_text = "\n\n".join(contexts)

        prompt = f"""
You are a strict RAG system answering questions from provided excerpts.

Rules:
1. Use ONLY the provided context excerpts. Do not use outside knowledge.
2. If the answer is not present, reply exactly: Not found in context
3. Write complete, well-formed sentences (no fragments).
4. Prefer bullet points for "benefits", "features", "steps", etc. If the context contains a bullet list, extract ALL items from that list.
5. Add citations using bracketed excerpt numbers like [1] or [2][3].
6. Every factual claim must have at least one citation.

Context excerpts:
{context_text}

Question:
{query}

Answer (with citations):
"""

        
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",   # ✅ fast + free
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    def generate_basic(self, message):
        """General-purpose chat for non-document mode using Groq free model."""
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise, friendly assistant. "
                        "Answer general questions clearly."
                    ),
                },
                {"role": "user", "content": message},
            ],
        )

        return response.choices[0].message.content