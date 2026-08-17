from src.pricing import embedding_cost, generation_cost


def test_embedding_and_generation_costs_are_separate_and_positive() -> None:
    indexing = embedding_cost(["uno dos tres", "cuatro cinco"])
    query = generation_cost("pregunta y contexto", "respuesta")
    assert indexing.input_tokens > 0 and indexing.output_tokens == 0
    assert query.input_tokens > 0 and query.output_tokens > 0
    assert indexing.estimated_usd > 0 and query.estimated_usd > 0
