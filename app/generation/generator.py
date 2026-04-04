from dotenv import load_dotenv

load_dotenv()

from groq import Groq
import os
print("API KEY:", os.getenv("GROQ_API_KEY"))

class Generator:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate(self, query, contexts):
        context_text = "\n\n".join(contexts)

        prompt = f"""
You are a strict RAG system.

Rules:
1. Answer ONLY using the provided context
2. Do NOT use prior knowledge
3. If answer is not in context, say: "Not found in context"
4. Be concise and factual

Context:
{context_text}

Question:
{query}

Answer:
"""

        
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",   # ✅ fast + free
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content