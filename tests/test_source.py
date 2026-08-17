from pathlib import Path

import pytest
import tiktoken

from src.source import SourceValidationError, load_records, record_to_chunk


SOURCE = Path(__file__).parents[1] / "data" / "faq_document.txt"


def test_source_meets_volume_and_traceability_contract() -> None:
    records = load_records(SOURCE)
    assert len([r for r in records if r.record_type == "bug"]) >= 15
    assert len([r for r in records if r.record_type == "test_case"]) >= 20
    ids = {record.id for record in records}
    assert all(set(record.related_ids) <= ids for record in records)
    assert len(ids) == len(records)


def test_each_record_becomes_one_complete_semantic_chunk() -> None:
    encoding = tiktoken.get_encoding("cl100k_base")
    records = load_records(SOURCE)
    for record in records:
        chunk = record_to_chunk(record)
        assert record.id in chunk
        assert record.module in chunk
        assert record.evidence_state in chunk
        assert 50 <= len(encoding.encode(chunk)) <= 500


def test_duplicate_id_is_rejected(tmp_path: Path) -> None:
    text = SOURCE.read_text(encoding="utf-8")
    first_record = text.split("\n===\n")[1]
    path = tmp_path / "duplicate.txt"
    path.write_text(text + "\n===\n" + first_record, encoding="utf-8")
    with pytest.raises(SourceValidationError, match="duplicados"):
        load_records(path)
