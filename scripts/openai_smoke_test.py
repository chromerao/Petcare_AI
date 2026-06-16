"""Optional paid smoke test for the configured OpenAI account."""

import asyncio

from docqa.core.config import get_settings
from docqa.providers.contracts import GenerationRequest
from docqa.providers.openai_responses import OpenAIResponsesProvider


async def main() -> None:
    settings = get_settings().model_copy(
        update={
            "openai_max_output_tokens": 64,
            "openai_store": False,
        }
    )
    provider = OpenAIResponsesProvider(settings)
    result = await provider.generate(
        GenerationRequest(
            instructions="Answer in Korean using one short sentence.",
            input_text="Reply that the API connection test succeeded.",
        )
    )

    print(f"model={result.model}")
    print(f"input_tokens={result.input_tokens}")
    print(f"output_tokens={result.output_tokens}")
    print(f"response={result.text}")


if __name__ == "__main__":
    asyncio.run(main())
