from providers.openai_provider import OpenAIProvider
from providers.openrouter_provider import OpenRouterProvider
from providers.anthropic_provider import AnthropicProvider
from providers.gemini_provider import GeminiProvider


def make_provider(name: str):
    norm = name.lower().replace("-", "_")
    if norm in ["openai", "openai_compatible", "compatible"]:
        return OpenAIProvider()
    if norm == "openrouter":
        return OpenRouterProvider()
    if norm == "anthropic":
        return AnthropicProvider()
    if norm == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unknown provider: {name}")
