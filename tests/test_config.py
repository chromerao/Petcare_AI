from pydantic import SecretStr

from docqa.core.config import Settings


def test_openai_defaults_are_bounded_and_do_not_expose_secret() -> None:
    settings = Settings(OPENAI_API_KEY="test-secret")

    assert settings.openai_configured is True
    assert settings.openai_model == "gpt-4.1-mini"
    assert settings.openai_max_output_tokens == 800
    assert settings.openai_store is False
    assert "test-secret" not in repr(settings)
    assert isinstance(settings.openai_api_key, SecretStr)


def test_openai_is_not_configured_without_a_key() -> None:
    settings = Settings(_env_file=None, OPENAI_API_KEY=None)

    assert settings.openai_configured is False


def test_local_cors_origins_include_react_and_streamlit_dev_servers() -> None:
    settings = Settings(_env_file=None, allowed_origins=["http://localhost:8501"])

    assert "http://localhost:5173" in settings.cors_origins
    assert "http://127.0.0.1:5173" in settings.cors_origins
    assert "http://localhost:8501" in settings.cors_origins
    assert settings.cors_origin_regex is not None


def test_production_cors_origins_do_not_add_dev_servers() -> None:
    settings = Settings(
        _env_file=None,
        environment="production",
        allowed_origins=["https://petcare.example.com"],
    )

    assert settings.cors_origins == ["https://petcare.example.com"]
    assert settings.cors_origin_regex is None
