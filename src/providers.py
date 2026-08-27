"""LangChain integrations for embeddings and generation, both live and injectable."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol, TypedDict

from langchain_core.embeddings import Embeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


SYSTEM_PROMPT = (
    "Sos un asistente de QA evidence-only. Respondé en español, de forma breve. "
    "Usá exclusivamente la evidencia recibida. Mencioná solamente IDs presentes. "
    "Citá sólo el ID principal que aparece al inicio de cada bloque recuperado; "
    "no cites IDs listados únicamente como relaciones. No inventes bugs, test cases, "
    "pasos, relaciones ni datos técnicos. Si la evidencia no alcanza, incluí una "
    "abstención explícita. Un smoke sugerido no es evidencia histórica."
)


class StructuredAnswer(TypedDict):
    """Internal output required from the model before building the public contract."""

    system_answer: str


class AnswerProvider(Protocol):
    """Minimum contract for generating a response from context."""

    def answer(self, question: str, context: str) -> str:
        """Answer a question using only the provided context."""

        ...


class DeterministicEmbeddingProvider(Embeddings):
    """Stable lexical embedding for offline tests; it does not replace the live provider."""

    _STOPWORDS = {"de", "del", "la", "las", "el", "los", "un", "una", "y", "o", "que",
                  "con", "sin", "por", "para", "en", "al", "se", "su", "sus", "es"}

    def __init__(self, dimensions: int = 1024) -> None:
        """Set the fixed dimension for test vectors."""
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate reproducible lexical vectors without network access."""
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for token in re.findall(r"[a-záéíóúñ0-9]+", text.lower()):
                if token in self._STOPWORDS:
                    continue
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimensions
                vector[index] += 1.0
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors

    def embed_query(self, text: str) -> list[float]:
        """Generate a query vector with the same strategy used for documents."""
        return self.embed_documents([text])[0]


def create_openai_embeddings(api_key: str, model: str) -> OpenAIEmbeddings:
    """Create the LangChain embeddings integration without making calls yet."""
    return OpenAIEmbeddings(api_key=api_key, model=model)


class LangChainAnswerProvider:
    """Run a LangChain chain with a prompt and structured output."""

    def __init__(self, chain: Runnable[dict[str, str], StructuredAnswer]) -> None:
        """Accept an injectable chain to keep tests fully offline."""
        self.chain = chain

    @classmethod
    def from_openai(cls, api_key: str, model: str) -> "LangChainAnswerProvider":
        """Compose ChatPromptTemplate, the Responses API, and Structured Outputs."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "Pregunta: {question}\n\nEvidencia:\n{context}"),
        ])
        llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            use_responses_api=True,
            reasoning_effort="none",
        )
        structured_llm = llm.with_structured_output(
            StructuredAnswer,
            method="json_schema",
        )
        return cls(prompt | structured_llm)

    def answer(self, question: str, context: str) -> str:
        """Invoke the chain and return only the validated internal response."""
        result = self.chain.invoke({"question": question, "context": context})
        answer = result.get("system_answer")
        if not isinstance(answer, str):
            raise ValueError("El modelo no devolvió system_answer como texto")
        return answer
