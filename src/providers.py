"""Integraciones LangChain para embeddings y generación, reales e inyectables."""

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
    """Salida interna exigida al modelo antes de construir el contrato público."""

    system_answer: str


class AnswerProvider(Protocol):
    """Contrato mínimo para generar una respuesta con contexto."""

    def answer(self, question: str, context: str) -> str:
        """Responde una pregunta usando únicamente el contexto."""

        ...


class DeterministicEmbeddingProvider(Embeddings):
    """Embedding lexical estable para tests offline; no reemplaza al proveedor real."""

    _STOPWORDS = {"de", "del", "la", "las", "el", "los", "un", "una", "y", "o", "que",
                  "con", "sin", "por", "para", "en", "al", "se", "su", "sus", "es"}

    def __init__(self, dimensions: int = 1024) -> None:
        """Define la dimensión fija de los vectores de prueba."""
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Genera vectores léxicos reproducibles sin usar red."""
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
        """Genera el vector de una consulta con la misma estrategia que los documentos."""
        return self.embed_documents([text])[0]


def create_openai_embeddings(api_key: str, model: str) -> OpenAIEmbeddings:
    """Crea la integración LangChain de embeddings sin realizar llamadas todavía."""
    return OpenAIEmbeddings(api_key=api_key, model=model)


class LangChainAnswerProvider:
    """Ejecuta una chain LangChain con prompt y salida estructurada."""

    def __init__(self, chain: Runnable[dict[str, str], StructuredAnswer]) -> None:
        """Recibe una chain inyectable para mantener las pruebas completamente offline."""
        self.chain = chain

    @classmethod
    def from_openai(cls, api_key: str, model: str) -> "LangChainAnswerProvider":
        """Compone ChatPromptTemplate, Responses API y Structured Outputs."""
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
        """Invoca la chain y devuelve solamente la respuesta interna validada."""
        result = self.chain.invoke({"question": question, "context": context})
        answer = result.get("system_answer")
        if not isinstance(answer, str):
            raise ValueError("El modelo no devolvió system_answer como texto")
        return answer
