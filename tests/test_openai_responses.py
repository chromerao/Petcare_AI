import asyncio
from typing import cast

import pytest
from openai import AsyncOpenAI

from docqa.core.config import Settings
from docqa.providers.contracts import (
    GenerationRequest,
    ProviderConfigurationError,
    ProviderResponseError,
)
from docqa.providers.openai_responses import OpenAIResponsesProvider


class FakeUsage:
    input_tokens = 42
    output_tokens = 17


class FakeResponse:
    output_text = "근거가 확인된 테스트 답변입니다."
    model = "gpt-4.1-mini-2025-04-14"
    usage = FakeUsage()


class FakeResponses:
    def __init__(self) -> None:
        self.last_request: dict[str, object] | None = None

    async def create(self, **kwargs: object) -> FakeResponse:
        self.last_request = kwargs
        return FakeResponse()


class FakeClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def test_openai_provider_applies_cost_and_storage_limits() -> None:
    settings = Settings(_env_file=None, OPENAI_API_KEY="test-secret")
    fake_client = FakeClient()
    provider = OpenAIResponsesProvider(settings, cast("AsyncOpenAI", fake_client))

    result = asyncio.run(
        provider.generate(
            GenerationRequest(
                instructions="Use only supplied evidence.",
                input_text="Synthetic evidence only.",
            )
        )
    )

    assert result.text == "근거가 확인된 테스트 답변입니다."
    assert result.input_tokens == 42
    assert result.output_tokens == 17
    assert fake_client.responses.last_request == {
        "model": "gpt-4.1-mini",
        "instructions": "Use only supplied evidence.",
        "input": "Synthetic evidence only.",
        "max_output_tokens": 800,
        "store": False,
    }


def test_openai_provider_rejects_oversized_input_before_api_call() -> None:
    settings = Settings(
        _env_file=None,
        OPENAI_API_KEY="test-secret",
        llm_max_input_characters=1000,
    )
    fake_client = FakeClient()
    provider = OpenAIResponsesProvider(settings, cast("AsyncOpenAI", fake_client))

    with pytest.raises(ProviderConfigurationError):
        asyncio.run(
            provider.generate(GenerationRequest(instructions="test", input_text="x" * 1001))
        )

    assert fake_client.responses.last_request is None


class EmptyFakeResponse(FakeResponse):
    output_text = "  "


class EmptyFakeResponses(FakeResponses):
    async def create(self, **kwargs: object) -> EmptyFakeResponse:
        self.last_request = kwargs
        return EmptyFakeResponse()


class EmptyFakeClient:
    def __init__(self) -> None:
        self.responses = EmptyFakeResponses()


def test_openai_provider_rejects_empty_model_output() -> None:
    settings = Settings(_env_file=None, OPENAI_API_KEY="test-secret")
    provider = OpenAIResponsesProvider(
        settings,
        cast("AsyncOpenAI", EmptyFakeClient()),
    )

    with pytest.raises(ProviderResponseError):
        asyncio.run(
            provider.generate(GenerationRequest(instructions="test", input_text="evidence"))
        )
