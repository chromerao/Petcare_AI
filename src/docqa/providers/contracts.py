from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GenerationRequest:
    instructions: str
    input_text: str


@dataclass(frozen=True)
class GenerationResult:
    text: str
    model: str
    input_tokens: int | None
    output_tokens: int | None


class TextGenerationProvider(Protocol):
    async def generate(self, request: GenerationRequest) -> GenerationResult: ...


class ProviderConfigurationError(RuntimeError):
    """Raised when a provider cannot be initialized safely."""


class ProviderTimeoutError(RuntimeError):
    """Raised when a provider exceeds the configured timeout."""


class ProviderResponseError(RuntimeError):
    """Raised when a provider returns no usable output."""
