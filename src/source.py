"""Loading and validation for the structured plain-text source document."""

from __future__ import annotations

from pathlib import Path
import re

from .models import QARecord


REQUIRED_FIELDS = {
    "ID", "TYPE", "MODULE", "TITLE", "RELATED_IDS", "FUNCTIONAL_DOMAIN",
    "SERVICE_OR_API", "ENDPOINT_OR_OPERATION", "OWNER_TEAM", "SUGGESTED_SMOKE",
    "SOURCE", "VALIDITY", "EVIDENCE_STATE", "CONTENT",
}
ID_PATTERN = re.compile(r"^(BUG|TC)-[A-Z]{3}-\d{3}$")


class SourceValidationError(ValueError):
    """Indicate that the source document does not meet its expected format."""

    pass


def _parse_block(block: str) -> QARecord:
    """Convert a validated text block into a QA record."""
    fields: dict[str, str] = {}
    current: str | None = None
    for raw_line in block.strip().splitlines():
        if ": " in raw_line and raw_line.split(": ", 1)[0] in REQUIRED_FIELDS:
            current, value = raw_line.split(": ", 1)
            fields[current] = value.strip()
        elif current == "CONTENT" and raw_line.strip():
            fields[current] += " " + raw_line.strip()
    missing = REQUIRED_FIELDS - fields.keys()
    if missing:
        raise SourceValidationError(f"Registro incompleto; faltan: {sorted(missing)}")
    return _record_from_fields(fields)


def _record_from_fields(fields: dict[str, str]) -> QARecord:
    """Validate fields and build the domain record."""

    record_id = fields["ID"]
    if not ID_PATTERN.fullmatch(record_id):
        raise SourceValidationError(f"ID inválido: {record_id}")
    expected_type = "bug" if record_id.startswith("BUG-") else "test_case"
    if fields["TYPE"] != expected_type:
        raise SourceValidationError(f"Tipo inconsistente para {record_id}")
    state = fields["EVIDENCE_STATE"]
    if state not in {"confirmado", "parcial", "desconocido"}:
        raise SourceValidationError(f"Estado de evidencia inválido en {record_id}")
    technical = [fields[name] for name in (
        "FUNCTIONAL_DOMAIN", "SERVICE_OR_API", "ENDPOINT_OR_OPERATION", "OWNER_TEAM"
    )]
    if state == "desconocido" and any(value != "desconocido" for value in technical):
        raise SourceValidationError(f"{record_id} declara datos para evidencia desconocida")
    if state == "confirmado" and any(value == "desconocido" for value in technical):
        raise SourceValidationError(f"{record_id} tiene evidencia confirmada incompleta")
    related = tuple(item.strip() for item in fields["RELATED_IDS"].split(",") if item.strip())
    return QARecord(
        id=record_id, record_type=expected_type, module=fields["MODULE"],
        title=fields["TITLE"], content=fields["CONTENT"], related_ids=related,
        functional_domain=fields["FUNCTIONAL_DOMAIN"], service_or_api=fields["SERVICE_OR_API"],
        endpoint_or_operation=fields["ENDPOINT_OR_OPERATION"], owner_team=fields["OWNER_TEAM"],
        suggested_smoke=fields["SUGGESTED_SMOKE"], source=fields["SOURCE"],
        validity=fields["VALIDITY"], evidence_state=state,  # type: ignore[arg-type]
    )


def load_records(path: Path) -> list[QARecord]:
    """Load the source and validate volume, IDs, and relationships."""
    text = path.read_text(encoding="utf-8")
    blocks = [block for block in text.split("\n===\n") if "ID: " in block]
    records = [_parse_block(block) for block in blocks]
    ids = [record.id for record in records]
    if len(ids) != len(set(ids)):
        raise SourceValidationError("La fuente contiene IDs duplicados")
    known = set(ids)
    for record in records:
        unknown = set(record.related_ids) - known
        if unknown:
            raise SourceValidationError(f"{record.id} referencia IDs inexistentes: {sorted(unknown)}")
    if len([r for r in records if r.record_type == "bug"]) < 15:
        raise SourceValidationError("La fuente requiere al menos 15 bugs")
    if len([r for r in records if r.record_type == "test_case"]) < 20:
        raise SourceValidationError("La fuente requiere al menos 20 test cases")
    if len(text.split()) < 1000:
        raise SourceValidationError("La fuente requiere al menos 1000 palabras")
    return records


def record_to_chunk(record: QARecord) -> str:
    """Convert a complete record into a semantic chunk."""
    related = ", ".join(record.related_ids) or "sin relaciones registradas"
    return (
        f"{record.id} | {record.record_type} | módulo {record.module}. "
        f"{record.title}. {record.content} Relaciones: {related}. "
        f"Dominio: {record.functional_domain}. Servicio/API: {record.service_or_api}. "
        f"Operación: {record.endpoint_or_operation}. Owner: {record.owner_team}. "
        f"Smoke sugerido: {record.suggested_smoke}. Fuente: {record.source}. "
        f"Vigencia: {record.validity}. Evidencia: {record.evidence_state}."
    )
