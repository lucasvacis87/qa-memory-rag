from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.technical_catalog import (
    CATALOG_FIELD_NAMES,
    EvidenceField,
    EvidenceState,
    SuggestedSmoke,
    TechnicalCatalogSchema,
    load_catalog_template,
    validate_catalog_fields,
)


def _empty_fields() -> dict[str, object]:
    template_path = Path(__file__).parents[1] / "data" / "technical_catalog_template.json"
    return json.loads(template_path.read_text(encoding="utf-8"))["fields"]


def test_schema_declares_only_the_approved_technical_fields() -> None:
    assert CATALOG_FIELD_NAMES == (
        "functional_domain",
        "service_or_api",
        "endpoint_or_operation",
        "owner_team",
        "suggested_smoke",
    )


def test_unknown_field_carries_no_invented_value_source_or_validity() -> None:
    field = EvidenceField(state=EvidenceState.UNKNOWN)

    assert field.value is None
    assert field.source is None
    assert field.validity is None


def test_unknown_field_rejects_invented_information() -> None:
    with pytest.raises(ValueError, match="desconocido"):
        EvidenceField(state=EvidenceState.UNKNOWN, value="transferencias")


def test_confirmed_field_requires_value_source_and_validity() -> None:
    field = EvidenceField(
        state=EvidenceState.CONFIRMED,
        value="transferencias",
        source="registro ficticio",
        validity="2026-08",
    )

    assert field.state is EvidenceState.CONFIRMED


def test_partial_field_preserves_only_available_information() -> None:
    field = EvidenceField(state=EvidenceState.PARTIAL, source="registro incompleto")

    assert field.value is None
    assert field.source == "registro incompleto"


def test_suggested_smoke_cannot_be_historical_evidence() -> None:
    with pytest.raises(ValueError, match="histórica"):
        SuggestedSmoke(
            evidence=EvidenceField(state=EvidenceState.UNKNOWN),
            is_historical_evidence=True,
        )


def test_schema_accepts_unknown_fields_without_creating_a_record() -> None:
    unknown = EvidenceField(state=EvidenceState.UNKNOWN)
    schema = TechnicalCatalogSchema(
        functional_domain=unknown,
        service_or_api=unknown,
        endpoint_or_operation=unknown,
        owner_team=unknown,
        suggested_smoke=SuggestedSmoke(evidence=unknown),
    )

    assert schema.suggested_smoke.label == "sugerido"


def test_empty_catalog_template_is_valid_and_contains_no_invented_data() -> None:
    template_path = Path(__file__).parents[1] / "data" / "technical_catalog_template.json"

    template = load_catalog_template(template_path)

    assert template.functional_domain.state is EvidenceState.UNKNOWN
    assert template.service_or_api.state is EvidenceState.UNKNOWN
    assert template.endpoint_or_operation.state is EvidenceState.UNKNOWN
    assert template.owner_team.state is EvidenceState.UNKNOWN
    assert template.suggested_smoke.evidence.state is EvidenceState.UNKNOWN
    assert template.suggested_smoke.is_historical_evidence is False


def test_future_entry_validation_accepts_a_partial_field_without_filling_gaps() -> None:
    fields = _empty_fields()
    fields["functional_domain"] = {
        "state": "parcial",
        "value": None,
        "source": "fuente disponible",
        "validity": None,
    }

    validated = validate_catalog_fields(fields)

    assert validated.functional_domain.state is EvidenceState.PARTIAL
    assert validated.functional_domain.value is None
    assert validated.functional_domain.source == "fuente disponible"


def test_future_entry_validation_rejects_confirmed_without_full_evidence() -> None:
    fields = _empty_fields()
    fields["service_or_api"] = {
        "state": "confirmado",
        "value": "dato declarado",
        "source": "fuente disponible",
        "validity": None,
    }

    with pytest.raises(ValueError, match="confirmado"):
        validate_catalog_fields(fields)


def test_future_entry_validation_rejects_unknown_with_data() -> None:
    fields = _empty_fields()
    fields["owner_team"] = {
        "state": "desconocido",
        "value": "dato no respaldado",
        "source": None,
        "validity": None,
    }

    with pytest.raises(ValueError, match="desconocido"):
        validate_catalog_fields(fields)


@pytest.mark.parametrize(
    "smoke_change",
    [
        {"label": "histórico"},
        {"is_historical_evidence": True},
    ],
)
def test_future_entry_validation_rejects_smoke_not_marked_as_suggested(
    smoke_change: dict[str, object],
) -> None:
    fields = _empty_fields()
    fields["suggested_smoke"].update(smoke_change)

    with pytest.raises(ValueError):
        validate_catalog_fields(fields)
