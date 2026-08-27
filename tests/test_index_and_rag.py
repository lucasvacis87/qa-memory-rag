from pathlib import Path

import pytest

from src.evaluation import evaluate
from src.index import IndexUnavailableError, QAIndex
from src.providers import DeterministicEmbeddingProvider
from src.rag import ABSTENTION, ExtractiveAnswerProvider, ask
from src.source import load_records


SOURCE = Path(__file__).parents[1] / "data" / "faq_document.txt"


class HallucinatingProvider:
    def answer(self, question: str, context: str) -> str:
        return "Ejecutar TC-XXX-999 por BUG-XXX-999."


def _index(tmp_path: Path) -> QAIndex:
    provider = DeterministicEmbeddingProvider()
    index = QAIndex(tmp_path / "chroma", "test_qa_memory", provider)
    assert index.rebuild(load_records(SOURCE)) == 37
    return index


def test_empty_langchain_chroma_collection_is_unavailable(tmp_path: Path) -> None:
    index = QAIndex(tmp_path / "empty-chroma", "empty", DeterministicEmbeddingProvider())
    with pytest.raises(IndexUnavailableError, match="build-index"):
        index.count()


def test_index_reopens_and_filters_types(tmp_path: Path) -> None:
    index = _index(tmp_path)
    reopened = QAIndex(tmp_path / "chroma", "test_qa_memory", DeterministicEmbeddingProvider())
    assert reopened.count() == 37
    bugs = reopened.search("transferencia rechazada descuenta saldo", "bug", threshold=0.0)
    tests = reopened.search("transferencia rechazada descuenta saldo", "test_case", threshold=0.0)
    assert 0 < len(bugs) <= 2 and all(chunk.record_type == "bug" for chunk in bugs)
    assert 0 < len(tests) <= 2 and all(chunk.record_type == "test_case" for chunk in tests)


def test_pipeline_contract_is_exact_and_ids_are_grounded(tmp_path: Path) -> None:
    response = ask(
        "Una transferencia rechazada descontó el saldo",
        _index(tmp_path), ExtractiveAnswerProvider(), threshold=0.0,
    )
    assert set(response.public_dict()) == {"user_question", "system_answer", "chunks_related"}
    assessment = evaluate(response, {"BUG-TRF-001", "TC-TRF-004"})
    assert assessment.valid_ids
    assert assessment.expected_evidence_found


def test_hallucinated_id_forces_safe_abstention(tmp_path: Path) -> None:
    response = ask("transferencia rechazada", _index(tmp_path), HallucinatingProvider(), threshold=0.0)
    assert response.system_answer == ABSTENTION


def test_high_threshold_produces_abstention(tmp_path: Path) -> None:
    response = ask("cultivo de orquídeas", _index(tmp_path), ExtractiveAnswerProvider(), threshold=1.01)
    assert response.system_answer == ABSTENTION
    assert response.chunks_related == ()
    assert evaluate(response, expect_abstention=True).score == 10
