"""Configuración local y segura para los futuros pasos de OpenAI.

Este módulo no crea clientes ni realiza llamadas de red. La carga de ``.env``
ocurre únicamente al invocar :func:`load_settings`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os
from pathlib import Path
import sys

from dotenv import load_dotenv


class ConfigurationError(ValueError):
    """Indica una configuración local incompleta sin incluir valores sensibles."""


@dataclass(frozen=True)
class Settings:
    """Valores necesarios antes de usar embeddings o generación en el futuro."""

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
_PLACEHOLDER_VALUES = {
    "your-key-here",
    "your-response-model",
    "change-me",
    "changeme",
    "placeholder",
    "definir_antes_del_primer_uso",
}


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        normalized in _PLACEHOLDER_VALUES
        or normalized.startswith("your-")
        or (normalized.startswith("<") and normalized.endswith(">"))
    )


def _read_required_value(name: str, value: str | None) -> str:
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
    """Valida valores ya cargados, sin leer archivos ni usar red."""

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
    """Carga y valida la configuración sin crear un cliente de OpenAI.

    Las variables del sistema tienen prioridad sobre ``.env`` para facilitar
    ejecución local y pruebas sin modificar archivos de secretos.
    """

    path = dotenv_path if dotenv_path is not None else Path.cwd() / ".env"
    load_dotenv(dotenv_path=path, override=False)
    return validate_settings({name: os.getenv(name) for name in _REQUIRED_VARIABLES})


def main() -> int:
    """Ejecuta un chequeo local de configuración sin usar red ni secretos."""

    try:
        load_settings()
    except ConfigurationError as error:
        print(f"Error de configuración: {error}", file=sys.stderr)
        return 2

    print("Configuración local validada. No se realizó ninguna llamada a OpenAI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
