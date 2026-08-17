"""Genera ejemplos y datos de demo sin red ni consumo de API."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import evaluate
from src.index import QAIndex
from src.providers import DeterministicEmbeddingProvider
from src.rag import ExtractiveAnswerProvider, ask
from src.source import load_records


CASES = [
    ("UC-01", "El usuario se bloquea antes del quinto intento", {"BUG-AUT-001"}, 0.0),
    ("UC-02", "Una transferencia aprobada no aparece en movimientos", {"BUG-MOV-001"}, 0.0),
    ("UC-03", "Una transferencia rechazada descuenta el saldo", {"BUG-TRF-001", "TC-TRF-004"}, 0.0),
    ("UC-04", "Un pago se duplica después de reintentar", {"BUG-PAG-001"}, 0.0),
    ("UC-05", "El límite de tarjeta cambia en la interfaz pero no en backend", {"BUG-TAR-001"}, 0.0),
    ("UC-06", "Una operación exitosa no genera comprobante ni notificación", {"BUG-NOT-001"}, 0.0),
    ("UC-07", "¿Qué regresión existente cubre el doble envío de transferencias?", {"BUG-TRF-002", "TC-TRF-001"}, 0.0),
    ("UC-08", "¿Cómo cultivo orquídeas en Marte?", set(), 1.01),
]


def main() -> None:
    """Regenera ejemplos públicos y datos de la demo sin usar APIs."""
    records = load_records(ROOT / "data" / "faq_document.txt")
    # Chroma mantiene archivos mapeados brevemente en Windows; la limpieza del
    # temporal no debe invalidar la generación ya completada.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as directory:
        index = QAIndex(Path(directory), "samples", DeterministicEmbeddingProvider())
        index.rebuild(records)
        samples = []
        demo_samples = []
        for case_id, question, expected_ids, threshold in CASES:
            response = ask(question, index, ExtractiveAnswerProvider(), threshold)
            public_response = response.public_dict()
            samples.append(public_response)
            demo_samples.append({
                "case_id": case_id,
                **public_response,
                "evaluation": evaluate(
                    response, expected_ids, expect_abstention=case_id == "UC-08"
                ).__dict__,
            })
    demo_payload = {"mode": "offline_deterministic", "samples": demo_samples}
    (ROOT / "outputs" / "sample_queries.json").write_text(
        json.dumps(samples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "docs" / "demo-data.js").write_text(
        "window.QA_MEMORY_SAMPLES = " + json.dumps(demo_payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
