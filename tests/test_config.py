from __future__ import annotations

import inspect
from pathlib import Path
import socket

import pytest

import src.config as config


VALID_VALUES = {
    "OPENAI_API_KEY": "offline-test-key",
    "EMBEDDING_MODEL": "text-embedding-3-small",
    "RESPONSE_MODEL": "offline-test-response-model",
}


def test_validate_settings_returns_typed_valid_configuration() -> None:
    settings = config.validate_settings(VALID_VALUES)

    assert settings == config.Settings(
        openai_api_key="offline-test-key",
        embedding_model="text-embedding-3-small",
        response_model="offline-test-response-model",
    )


@pytest.mark.parametrize(
    ("variable", "invalid_value"),
    [
        ("OPENAI_API_KEY", None),
        ("OPENAI_API_KEY", "   "),
        ("OPENAI_API_KEY", "your-key-here"),
        ("EMBEDDING_MODEL", None),
        ("EMBEDDING_MODEL", "   "),
        ("EMBEDDING_MODEL", "your-embedding-model"),
        ("RESPONSE_MODEL", None),
        ("RESPONSE_MODEL", "   "),
        ("RESPONSE_MODEL", "your-response-model"),
    ],
)
def test_validate_settings_rejects_missing_empty_and_placeholder_values(
    variable: str, invalid_value: str | None
) -> None:
    values = {**VALID_VALUES, variable: invalid_value}

    with pytest.raises(config.ConfigurationError, match=variable) as error:
        config.validate_settings(values)

    assert "offline-test-key" not in str(error.value)


def test_load_settings_does_not_create_client_or_open_network_connection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    load_dotenv_calls: list[dict[str, object]] = []

    def record_dotenv_load(**kwargs: object) -> bool:
        load_dotenv_calls.append(kwargs)
        return False

    def forbid_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("La configuración no debe abrir conexiones de red.")

    monkeypatch.setattr(config, "load_dotenv", record_dotenv_load)
    monkeypatch.setattr(socket, "create_connection", forbid_network)
    monkeypatch.setattr(socket, "socket", forbid_network)
    for name, value in VALID_VALUES.items():
        monkeypatch.setenv(name, value)

    settings = config.load_settings()

    assert settings.openai_api_key == "offline-test-key"
    assert load_dotenv_calls == [{"dotenv_path": Path.cwd() / ".env", "override": False}]
    source = inspect.getsource(config)
    assert "from openai" not in source
    assert "OpenAI(" not in source


def test_main_reports_a_safe_configuration_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        config,
        "load_settings",
        lambda: (_ for _ in ()).throw(
            config.ConfigurationError("Falta configurar OPENAI_API_KEY.")
        ),
    )

    exit_code = config.main()

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "OPENAI_API_KEY" in captured.err
    assert captured.out == ""


def test_main_confirms_offline_validation(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(config, "load_settings", lambda: config.Settings(**{
        "openai_api_key": "offline-test-key",
        "embedding_model": "text-embedding-3-small",
        "response_model": "offline-test-response-model",
    }))

    exit_code = config.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "No se realizó ninguna llamada a OpenAI" in captured.out
    assert captured.err == ""
