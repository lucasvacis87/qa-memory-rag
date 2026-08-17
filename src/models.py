"""Modelos de dominio y contrato público del QA Memory RAG."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


RecordType = Literal["bug", "test_case"]
EvidenceState = Literal["confirmado", "parcial", "desconocido"]


@dataclass(frozen=True)
class QARecord:
    id: str
    record_type: RecordType
    module: str
    title: str
    content: str
    related_ids: tuple[str, ...]
    functional_domain: str
    service_or_api: str
    endpoint_or_operation: str
    owner_team: str
    suggested_smoke: str
    source: str
    validity: str
    evidence_state: EvidenceState

    def metadata(self) -> dict[str, str]:
        return {
            "id": self.id,
            "type": self.record_type,
            "module": self.module,
            "title": self.title,
            "related_ids": ",".join(self.related_ids),
            "functional_domain": self.functional_domain,
            "service_or_api": self.service_or_api,
            "endpoint_or_operation": self.endpoint_or_operation,
            "owner_team": self.owner_team,
            "suggested_smoke": self.suggested_smoke,
            "source": self.source,
            "validity": self.validity,
            "evidence_state": self.evidence_state,
        }


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    record_type: RecordType
    module: str
    content: str
    score: float
    metadata: dict[str, str]

    def public_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.record_type,
            "module": self.module,
            "content": self.content,
            "score": round(self.score, 4),
            "metadata": dict(sorted(self.metadata.items())),
        }


@dataclass(frozen=True)
class RAGResponse:
    user_question: str
    system_answer: str
    chunks_related: tuple[RetrievedChunk, ...]

    def public_dict(self) -> dict[str, Any]:
        return {
            "user_question": self.user_question,
            "system_answer": self.system_answer,
            "chunks_related": [chunk.public_dict() for chunk in self.chunks_related],
        }

    def assert_public_contract(self) -> None:
        assert set(self.public_dict()) == {
            "user_question", "system_answer", "chunks_related"
        }
