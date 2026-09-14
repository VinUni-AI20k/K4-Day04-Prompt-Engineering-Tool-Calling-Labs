from __future__ import annotations

import json
import os
from typing import Any

from providers.base import ModelResponse
from providers.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    """Groq uses an OpenAI-compatible Chat Completions surface."""

    def __init__(self) -> None:
        super().__init__(
            api_key_env="GROQ_API_KEY",
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            default_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        )

    def complete(self, messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None, **kwargs: Any) -> ModelResponse:
        try:
            return super().complete(messages, tools, **kwargs)
        except Exception as exc:
            text = _json_pseudo_tool_text(exc)
            if text is None:
                raise
            return ModelResponse(text=text, tool_calls=[], raw={"recovered_from": "groq_json_pseudo_tool"})


def _json_pseudo_tool_text(exc: Exception) -> str | None:
    """gpt-oss sometimes wraps a JSON-formatted *text* reply in a fake tool named
    "json"; Groq rejects that with 400 tool_use_failed. Recover only that exact
    case as plain text. Any other undeclared tool call still raises."""
    body = getattr(exc, "body", None)
    error = body.get("error", body) if isinstance(body, dict) else None
    if not isinstance(error, dict) or error.get("code") != "tool_use_failed":
        return None
    try:
        generation = json.loads(error.get("failed_generation") or "")
    except ValueError:
        return None
    if not isinstance(generation, dict) or generation.get("name") != "json":
        return None
    return json.dumps(generation.get("arguments"), ensure_ascii=False)
