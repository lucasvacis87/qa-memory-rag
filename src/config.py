"""Safe local configuration for OpenAI and Chroma.

This module does not create clients or make network calls. ``.env`` loading
only occurs when :func:`load_settings` is invoked.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os
from pathlib import Path
import sys

from dotenv import load_dotenv


class ConfigurationError(ValueError):
    """Indicate incomplete local configuration without including sensitive values."""


@dataclass(frozen=True)
class Settings:
    """Values required for embeddings, generation, and local storage."""

    openai_api_key: str
    embedding_model: str
    response_model: str
    chroma_path: str = "chroma_db"
    collection_name: str = "qa_memory"
    relevance_threshold: float = 0.20


_REQUIRED_VARIABLES = (
    "OPENAI_API_KEY",
    "EMBEDDING_MODEL",
    "RESPONSE_MODEL",
)
_OPTIONAL_VARIABLES = (
    "CHROMA_PATH",
    "COLLECTION_NAME",
    "RELEVANCE_THRESHOLD",
)
_PLACEHOLDER_VALUES = {
    "your-key-here",
    "your-response-model",
    "change-me",
    "changeme",
    "placeholder",
    "definir_antes_del_primer_uso",
}


def _is_placeholder(value: str) -> bool:
    """Determine whether a value retains placeholder text."""
    normalized = value.strip().lower()
    return (
        normalized in _PLACEHOLDER_VALUES
        or normalized.startswith("your-")
        or (normalized.startswith("<") and normalized.endswith(">"))
    )


def _read_required_value(name: str, value: str | None) -> str:
    """Get a required variable or explain how to configure it."""
    if value is None or not value.strip():
        raise ConfigurationError(
            f"Falta configurar {name}. Completá tu archivo .env local antes de continuar."
        )
    if _is_placeholder(value):
        raise ConfigurationError(
            f"{name} contiene un placeholder. Reemplazalo sólo en tu archivo .env local."
        )
    return value.strip()


def validate_settings(values: Mapping[str, str | None]) -> Settings:
    """Validate loaded values without reading files or using the network."""

    validated = {
        name: _read_required_value(name, values.get(name)) for name in _REQUIRED_VARIABLES
    }
    return Settings(
        openai_api_key=validated["OPENAI_API_KEY"],
        embedding_model=validated["EMBEDDING_MODEL"],
        response_model=validated["RESPONSE_MODEL"],
        chroma_path=(values.get("CHROMA_PATH") or "chroma_db").strip(),
        collection_name=(values.get("COLLECTION_NAME") or "qa_memory").strip(),
        relevance_threshold=float(values.get("RELEVANCE_THRESHOLD") or "0.20"),
    )


def load_settings(dotenv_path: Path | None = None) -> Settings:
    """Load and validate configuration without creating an OpenAI client.

    System variables take precedence over ``.env`` to support local execution
    and testing without changing secret files.
    """

    path = dotenv_path if dotenv_path is not None else Path.cwd() / ".env"
    load_dotenv(dotenv_path=path, override=False)
    names = _REQUIRED_VARIABLES + _OPTIONAL_VARIABLES
    return validate_settings({name: os.getenv(name) for name in names})


def main() -> int:
    """Run a local configuration check without using the network or secrets."""

    try:
        load_settings()
    except ConfigurationError as error:
        print(f"Error de configuración: {error}", file=sys.stderr)
        return 2

    print("Configuración local validada. No se realizó ninguna llamada a OpenAI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
