from pathlib import Path

import pytest

from src.index import QAIndex
from src.providers import DeterministicEmbeddingProvider
from src.rag import ExtractiveAnswerProvider, ask
from src.source import load_records


SOURCE = Path(__file__).parents[1] / "data" / "faq_document.txt"
GOLDEN_CASES = [
    ("El usuario se bloquea antes del quinto intento", {"BUG-AUT-001"}),
    ("Una transferencia aprobada no aparece en movimientos", {"BUG-MOV-001"}),
    ("Una transferencia rechazada descuenta el saldo", {"BUG-TRF-001", "TC-TRF-004"}),
    ("Un pago se duplica después de reintentar", {"BUG-PAG-001"}),
    ("El límite de tarjeta cambia en interfaz pero no backend", {"BUG-TAR-001"}),
    ("Una operación exitosa no genera comprobante", {"BUG-NOT-001"}),
]


@pytest.fixture(scope="module")
def golden_index(tmp_path_factory: pytest.TempPathFactory) -> QAIndex:
    index = QAIndex(
        tmp_path_factory.mktemp("golden-chroma"), "golden",
        DeterministicEmbeddingProvider(),
    )
    index.rebuild(load_records(SOURCE))
    return index


def test_at_least_eighty_percent_of_golden_queries_recover_expected_evidence(
    golden_index: QAIndex,
) -> None:
    hits = 0
    for question, expected in GOLDEN_CASES:
        response = ask(question, golden_index, ExtractiveAnswerProvider(), threshold=0.0)
        hits += bool(expected & {chunk.id for chunk in response.chunks_related})
    assert hits / len(GOLDEN_CASES) >= 0.8
