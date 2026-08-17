"""Conteo y estimación transparente de costos de API."""

from __future__ import annotations

from dataclasses import dataclass

import tiktoken


EMBEDDING_USD_PER_MILLION = 0.02
GENERATION_INPUT_USD_PER_MILLION = 0.20
GENERATION_OUTPUT_USD_PER_MILLION = 1.25


@dataclass(frozen=True)
class UsageEstimate:
    input_tokens: int
    output_tokens: int
    estimated_usd: float


def count_tokens(text: str, model: str = "text-embedding-3-small") -> int:
    """Cuenta tokens con la codificación del modelo indicado."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("o200k_base")
    return len(encoding.encode(text))


def embedding_cost(texts: list[str]) -> UsageEstimate:
    """Estima tokens y costo de indexar una lista de textos."""
    tokens = sum(count_tokens(text) for text in texts)
    return UsageEstimate(tokens, 0, tokens * EMBEDDING_USD_PER_MILLION / 1_000_000)


def generation_cost(input_text: str, output_text: str) -> UsageEstimate:
    """Estima por separado el costo de entrada y salida del LLM."""
    input_tokens = count_tokens(input_text, "gpt-5.4-nano")
    output_tokens = count_tokens(output_text, "gpt-5.4-nano")
    cost = (input_tokens * GENERATION_INPUT_USD_PER_MILLION +
            output_tokens * GENERATION_OUTPUT_USD_PER_MILLION) / 1_000_000
    return UsageEstimate(input_tokens, output_tokens, cost)
