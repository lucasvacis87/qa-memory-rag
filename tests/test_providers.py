from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
import pytest

import src.providers as providers
from src.providers import (
    DeterministicEmbeddingProvider,
    LangChainAnswerProvider,
    create_openai_embeddings,
)


def test_deterministic_embeddings_follow_langchain_interface() -> None:
    embeddings = DeterministicEmbeddingProvider(dimensions=64)
    documents = embeddings.embed_documents(["transferencia rechazada", "pago duplicado"])

    assert len(documents) == 2
    assert all(len(vector) == 64 for vector in documents)
    assert embeddings.embed_query("transferencia rechazada") == documents[0]


def test_answer_provider_accepts_an_offline_langchain_runnable() -> None:
    chain = RunnableLambda(
        lambda values: {"system_answer": f"BUG-TRF-001: {values['question']}"}
    )
    provider = LangChainAnswerProvider(chain)

    assert provider.answer("¿Qué antecedente existe?", "BUG-TRF-001") == (
        "BUG-TRF-001: ¿Qué antecedente existe?"
    )


def test_answer_provider_rejects_invalid_structured_output() -> None:
    provider = LangChainAnswerProvider(RunnableLambda(lambda _: {"system_answer": 123}))

    with pytest.raises(ValueError, match="system_answer"):
        provider.answer("pregunta", "contexto")


def test_openai_factory_builds_prompt_responses_api_and_json_schema(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeChatOpenAI:
        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

        def with_structured_output(self, schema, method: str):
            captured["schema"] = schema
            captured["method"] = method

            def answer(prompt_value):
                messages = prompt_value.to_messages()
                captured["messages"] = messages
                return {"system_answer": "BUG-TRF-001 está respaldado."}

            return RunnableLambda(answer)

    monkeypatch.setattr(providers, "ChatOpenAI", FakeChatOpenAI)
    provider = LangChainAnswerProvider.from_openai("test-key", "gpt-5.4-nano")

    assert provider.answer("pregunta de prueba", "BUG-TRF-001 | evidencia") == (
        "BUG-TRF-001 está respaldado."
    )
    assert captured["method"] == "json_schema"
    assert captured["kwargs"] == {
        "api_key": "test-key",
        "model": "gpt-5.4-nano",
        "use_responses_api": True,
        "reasoning_effort": "none",
    }
    messages = captured["messages"]
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    assert "evidence-only" in messages[0].content
    assert "pregunta de prueba" in messages[1].content
    assert "BUG-TRF-001 | evidencia" in messages[1].content


def test_openai_embeddings_factory_is_lazy() -> None:
    embeddings = create_openai_embeddings("test-key", "text-embedding-3-small")

    assert embeddings.model == "text-embedding-3-small"
