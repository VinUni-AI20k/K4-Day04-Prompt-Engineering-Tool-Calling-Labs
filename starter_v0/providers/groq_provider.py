from __future__ import annotations

import json
import os
import re
import time
from typing import Any

from providers.base import ModelResponse
from providers.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    """Groq uses an OpenAI-compatible Chat Completions surface."""

    def __init__(self) -> None:
        super().__init__(
            api_key_env="GROQ_API_KEY",
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            default_model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
        )

    def complete(self, messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None, **kwargs: Any) -> ModelResponse:
        for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
            try:
                return super().complete(messages, tools, **kwargs)
            except Exception as exc:
                if getattr(exc, "status_code", None) == 429 and attempt < MAX_RATE_LIMIT_RETRIES:
                    # Free tier has a small tokens-per-minute budget; wait instead of failing the case.
                    time.sleep(_retry_after_seconds(exc, attempt))
                    continue
                text = _json_pseudo_tool_text(exc)
                if text is None:
                    if _is_malformed_tool_call(exc) and attempt < MAX_MALFORMED_RETRIES:
                        # Groq's parser rejected a garbled generation; resample instead of failing the case.
                        continue
                    raise
                return ModelResponse(text=text, tool_calls=[], raw={"recovered_from": "groq_json_pseudo_tool"})
        raise AssertionError("unreachable")


MAX_RATE_LIMIT_RETRIES = 6
MAX_MALFORMED_RETRIES = 2


def _is_malformed_tool_call(exc: Exception) -> bool:
    body = getattr(exc, "body", None)
    error = body.get("error", body) if isinstance(body, dict) else None
    return isinstance(error, dict) and error.get("code") == "tool_use_failed"


def _retry_after_seconds(exc: Exception, attempt: int) -> float:
    match = re.search(r"try again in ([\d.]+)s", str(exc))
    return (float(match.group(1)) if match else 5.0 * (attempt + 1)) + 1.0


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
