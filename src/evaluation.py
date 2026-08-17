"""Evaluación offline determinística de trazabilidad y relevancia."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .models import RAGResponse
from .rag import ABSTENTION, ID_PATTERN


@dataclass(frozen=True)
class Evaluation:
    score: float
    valid_ids: bool
    expected_evidence_found: bool
    abstention_correct: bool
    justification: str


def evaluate(
    response: RAGResponse, expected_ids: set[str] | None = None,
    expect_abstention: bool | None = None,
) -> Evaluation:
    """Puntúa trazabilidad, evidencia esperada y abstención."""
    available = {chunk.id for chunk in response.chunks_related}
    cited = set(ID_PATTERN.findall(response.system_answer))
    valid_ids = cited <= available
    expected = expected_ids or set()
    expected_found = not expected or bool(expected & available)
    abstained = response.system_answer == ABSTENTION
    if expect_abstention is None:
        expect_abstention = not response.chunks_related
    abstention_correct = abstained == expect_abstention
    points = 4 * valid_ids + 3 * expected_found + 3 * abstention_correct
    reasons = [
        "IDs válidos" if valid_ids else "hay IDs no recuperados",
        "evidencia esperada presente" if expected_found else "falta evidencia esperada",
        "abstención correcta" if abstention_correct else "abstención incorrecta",
    ]
    return Evaluation(float(points), valid_ids, expected_found, abstention_correct, "; ".join(reasons))
