from openai import APITimeoutError, AsyncOpenAI

from docqa.core.config import Settings
from docqa.providers.contracts import (
    GenerationRequest,
    GenerationResult,
    ProviderConfigurationError,
    ProviderResponseError,
    ProviderTimeoutError,
)


class OpenAIResponsesProvider:
    """Small, bounded adapter around the OpenAI Responses API."""

    def __init__(self, settings: Settings, client: AsyncOpenAI | None = None) -> None:
        self._settings = settings
        if client is not None:
            self._client = client
            return

        if settings.openai_api_key is None or not settings.openai_configured:
            raise ProviderConfigurationError("OpenAI API key is not configured.")

        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
            timeout=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if len(request.input_text) > self._settings.llm_max_input_characters:
            raise ProviderConfigurationError("Model input exceeds the configured character limit.")

        try:
            response = await self._client.responses.create(
                model=self._settings.openai_model,
                instructions=request.instructions,
                input=request.input_text,
                max_output_tokens=self._settings.openai_max_output_tokens,
                store=self._settings.openai_store,
            )
        except APITimeoutError as exc:
            raise ProviderTimeoutError("The language model request timed out.") from exc

        text = response.output_text.strip()
        if not text:
            raise ProviderResponseError("The language model returned no text.")

        usage = response.usage
        return GenerationResult(
            text=text,
            model=response.model,
            input_tokens=usage.input_tokens if usage is not None else None,
            output_tokens=usage.output_tokens if usage is not None else None,
        )
