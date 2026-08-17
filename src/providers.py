"""Adaptadores para embeddings y generación, reales e inyectables."""

from __future__ import annotations

from collections.abc import Sequence
import hashlib
import json
import math
import re
from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class AnswerProvider(Protocol):
    def answer(self, question: str, context: str) -> str: ...


class DeterministicEmbeddingProvider:
    """Embedding lexical estable para tests offline; no reemplaza al proveedor real."""

    _STOPWORDS = {"de", "del", "la", "las", "el", "los", "un", "una", "y", "o", "que",
                  "con", "sin", "por", "para", "en", "al", "se", "su", "sus", "es"}

    def __init__(self, dimensions: int = 1024) -> None:
        self.dimensions = dimensions

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
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


class OpenAIEmbeddingProvider:
    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=list(texts))
        return [item.embedding for item in response.data]


class OpenAIAnswerProvider:
    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def answer(self, question: str, context: str) -> str:
        prompt = (
            "Sos un asistente de QA evidence-only. Respondé en español, de forma breve. "
            "Usá exclusivamente la evidencia recibida. Mencioná solamente IDs presentes. "
            "Citá sólo el ID principal que aparece al inicio de cada bloque recuperado; "
            "no cites IDs listados únicamente como relaciones. "
            "No inventes bugs, test cases, pasos, relaciones ni datos técnicos. Si la evidencia "
            "no alcanza, incluí una abstención explícita. Un smoke sugerido no es evidencia histórica.\n\n"
            f"Pregunta: {question}\n\nEvidencia:\n{context}"
        )
        response = self.client.responses.create(
            model=self.model,
            reasoning={"effort": "none"},
            input=prompt,
            text={"format": {"type": "json_schema", "name": "qa_answer", "strict": True,
                "schema": {"type": "object", "properties": {"system_answer": {"type": "string"}},
                           "required": ["system_answer"], "additionalProperties": False}}},
        )
        return json.loads(response.output_text)["system_answer"]
