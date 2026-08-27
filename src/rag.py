"""RAG orchestration with deterministic validation after generation."""

from __future__ import annotations

import re

from .index import QAIndex
from .models import RAGResponse, RetrievedChunk
from .providers import AnswerProvider


ID_PATTERN = re.compile(r"\b(?:BUG|TC)-[A-Z]{3}-\d{3}\b")
ABSTENTION = "No hay evidencia suficiente en la base de conocimiento para responder con trazabilidad."


def _context(chunks: list[RetrievedChunk]) -> str:
    """Join retrieved chunks to form the model context."""
    return "\n\n".join(chunk.content for chunk in chunks)


def _answer_is_grounded(answer: str, chunks: list[RetrievedChunk]) -> bool:
    """Verify that the response cites only retrieved IDs."""
    available = {chunk.id for chunk in chunks}
    cited = set(ID_PATTERN.findall(answer))
    return bool(cited) and cited <= available


def ask(
    question: str, index: QAIndex, answer_provider: AnswerProvider,
    threshold: float = 0.45,
) -> RAGResponse:
    """Retrieve evidence, generate a response, and validate its IDs."""
    if not question.strip():
        raise ValueError("La pregunta no puede estar vacía")
    bugs = index.search(question, "bug", threshold=threshold)
    tests = index.search(question, "test_case", threshold=threshold)
    chunks = bugs + tests
    if not chunks:
        return RAGResponse(question, ABSTENTION, ())
    answer = answer_provider.answer(question, _context(chunks)).strip()
    if not _answer_is_grounded(answer, chunks):
        answer = ABSTENTION
    response = RAGResponse(question, answer, tuple(chunks))
    response.assert_public_contract()
    return response


class ExtractiveAnswerProvider:
    """Offline generator for evidence-only tests and reproducible demos."""

    def answer(self, question: str, context: str) -> str:
        """Summarize retrieved IDs for demos and offline tests."""
        ids = list(dict.fromkeys(re.findall(r"(?m)^(?:BUG|TC)-[A-Z]{3}-\d{3}", context)))
        selected = ids[:4]
        if not selected:
            return ABSTENTION
        return (
            f"La evidencia recuperada ({', '.join(selected)}) contiene antecedentes y cobertura "
            "relacionados. Revisá esos registros y ejecutá únicamente los test cases citados; "
            "los datos técnicos deben interpretarse según su estado de evidencia."
        )
