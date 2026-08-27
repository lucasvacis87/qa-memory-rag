"""Reproducible command-line interface for building, querying, and evaluating."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .config import ConfigurationError, Settings, load_settings
from .evaluation import evaluate
from .index import IndexUnavailableError, QAIndex
from .pricing import embedding_cost
from .providers import LangChainAnswerProvider, create_openai_embeddings
from .rag import ask
from .source import load_records, record_to_chunk


ROOT = Path(__file__).parents[1]


def _runtime() -> tuple[Settings, QAIndex]:
    """Create the configuration and index used by the command-line interface."""
    settings = load_settings(ROOT / ".env")
    embeddings = create_openai_embeddings(settings.openai_api_key, settings.embedding_model)
    return settings, QAIndex(ROOT / settings.chroma_path, settings.collection_name, embeddings)


def _parse_arguments(argv: list[str] | None) -> argparse.Namespace:
    """Configure the command-line interface and return validated arguments."""

    parser = argparse.ArgumentParser(description="QA Memory RAG evidence-only")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate-source")
    commands.add_parser("build-index")
    query = commands.add_parser("query")
    query.add_argument("question")
    query.add_argument("--evaluate", action="store_true")
    return parser.parse_args(argv)


def _run_command(args: argparse.Namespace) -> None:
    """Run a subcommand and write its result."""

    records = load_records(ROOT / "data" / "faq_document.txt")
    if args.command == "validate-source":
        print(json.dumps({"records": len(records), "bugs": sum(r.record_type == "bug" for r in records),
                          "test_cases": sum(r.record_type == "test_case" for r in records)}, ensure_ascii=False))
        return
    settings, index = _runtime()
    if args.command == "build-index":
        estimate = embedding_cost([record_to_chunk(record) for record in records])
        count = index.rebuild(records)
        print(json.dumps({"indexed": count, "embedding_model": settings.embedding_model,
                          "estimated_tokens": estimate.input_tokens,
                          "estimated_usd": round(estimate.estimated_usd, 8)}, ensure_ascii=False))
        return
    provider = LangChainAnswerProvider.from_openai(
        settings.openai_api_key,
        settings.response_model,
    )
    response = ask(args.question, index, provider, settings.relevance_threshold)
    if args.evaluate:
        print(json.dumps({"evaluation": evaluate(response).__dict__}, ensure_ascii=False), file=sys.stderr)
    print(json.dumps(response.public_dict(), ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface and convert errors to exit codes."""

    try:
        _run_command(_parse_arguments(argv))
        return 0
    except (ConfigurationError, IndexUnavailableError, ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    except Exception as error:
        print(f"Error operativo: {type(error).__name__}: {error}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
