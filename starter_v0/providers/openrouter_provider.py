from __future__ import annotations

import os
from providers.openai_provider import OpenAIProvider


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter uses an OpenAI-compatible Chat Completions surface."""

    def __init__(self) -> None:
        super().__init__(
            api_key_env="GEMINI_API_KEY",
            base_url=os.getenv("GEMINI_BASE_URL"),
            default_model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
        )
