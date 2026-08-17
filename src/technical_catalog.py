"""Esquema y lectura local del catálogo técnico *evidence-only*.

No incluye registros ficticios ni integraciones RAG. Su propósito es impedir
que una futura fuente complete datos técnicos por inferencia.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path
from typing import Any, Mapping


class EvidenceState(StrEnum):
    """Grado de respaldo disponible para un dato técnico."""

    CONFIRMED = "confirmado"
    PARTIAL = "parcial"
    UNKNOWN = "desconocido"


@dataclass(frozen=True)
class EvidenceField:
    """Un dato técnico y el respaldo que permite conservarlo.

    ``unknown`` representa ausencia de información: no puede transportar un
    valor, una fuente ni una vigencia. ``confirmed`` exige los tres. Un valor
    ``partial`` conserva sólo la porción disponible, sin completar huecos.
    """

    state: EvidenceState
    value: str | None = None
    source: str | None = None
    validity: str | None = None

    def __post_init__(self) -> None:
        values = (self.value, self.source, self.validity)

        if self.state is EvidenceState.UNKNOWN and any(values):
            raise ValueError("Un dato desconocido no puede incluir información inferida.")

        if self.state is EvidenceState.CONFIRMED and not all(values):
            raise ValueError(
                "Un dato confirmado requiere valor, fuente y vigencia explícitos."
            )

        if self.state is EvidenceState.PARTIAL and not any(values):
            raise ValueError("Un dato parcial debe conservar la información disponible.")


@dataclass(frozen=True)
class SuggestedSmoke:
    """Validación sugerida, separada explícitamente de evidencia histórica."""

    evidence: EvidenceField
    label: str = "sugerido"
    is_historical_evidence: bool = False

    def __post_init__(self) -> None:
        if self.label != "sugerido":
            raise ValueError("El smoke debe etiquetarse explícitamente como sugerido.")
        if self.is_historical_evidence:
            raise ValueError("Un smoke sugerido no puede presentarse como evidencia histórica.")


@dataclass(frozen=True)
class TechnicalCatalogSchema:
    """Campos técnicos que una futura evidencia QA podrá declarar.

    La clase describe un único esquema; todavía no representa bugs, test cases
    ni relaciones entre ellos. Cada campo admite ``unknown`` para evitar
    inventar vínculos o detalles técnicos inexistentes.
    """

    functional_domain: EvidenceField
    service_or_api: EvidenceField
    endpoint_or_operation: EvidenceField
    owner_team: EvidenceField
    suggested_smoke: SuggestedSmoke


CATALOG_FIELD_NAMES = (
    "functional_domain",
    "service_or_api",
    "endpoint_or_operation",
    "owner_team",
    "suggested_smoke",
)


def _read_evidence_field(raw_field: Mapping[str, Any]) -> EvidenceField:
    """Convierte un campo serializado en un campo validado."""

    return EvidenceField(
        state=EvidenceState(raw_field["state"]),
        value=raw_field.get("value"),
        source=raw_field.get("source"),
        validity=raw_field.get("validity"),
    )


def validate_catalog_fields(
    raw_fields: Mapping[str, Mapping[str, Any]],
) -> TechnicalCatalogSchema:
    """Valida una futura entrada técnica en memoria, sin guardarla.

    Recibe solamente los campos del catálogo y devuelve su forma validada. No
    crea registros QA, no escribe archivos y no completa valores ausentes.
    """

    if set(raw_fields) != set(CATALOG_FIELD_NAMES):
        raise ValueError("La entrada debe contener exactamente los campos técnicos aprobados.")

    smoke = raw_fields["suggested_smoke"]
    return TechnicalCatalogSchema(
        functional_domain=_read_evidence_field(raw_fields["functional_domain"]),
        service_or_api=_read_evidence_field(raw_fields["service_or_api"]),
        endpoint_or_operation=_read_evidence_field(raw_fields["endpoint_or_operation"]),
        owner_team=_read_evidence_field(raw_fields["owner_team"]),
        suggested_smoke=SuggestedSmoke(
            evidence=_read_evidence_field(smoke["evidence"]),
            label=smoke.get("label", "sugerido"),
            is_historical_evidence=smoke.get("is_historical_evidence", False),
        ),
    )


def load_catalog_template(path: Path) -> TechnicalCatalogSchema:
    """Lee y valida una plantilla vacía local, sin cargar registros QA.

    La plantilla se limita al esquema técnico. No representa bugs, test cases,
    endpoints concretos ni información de una integración externa.
    """

    raw_template = json.loads(path.read_text(encoding="utf-8"))
    raw_fields = raw_template["fields"]

    return validate_catalog_fields(raw_fields)
