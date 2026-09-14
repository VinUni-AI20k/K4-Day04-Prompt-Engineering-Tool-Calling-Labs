from __future__ import annotations

import json
import os
import time
from typing import Any

from providers.base import ModelResponse, ToolCall


class OpenAIProvider:
    """OpenAI Chat Completions provider with normalized tool_calls output."""

    def __init__(
        self,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
    ) -> None:
        self.api_key_env = api_key_env
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.default_model = default_model

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        try:
            from openai import OpenAI, APIStatusError, APIConnectionError
        except ImportError as exc:
            raise RuntimeError("Install live provider dependency first: pip install openai") from exc

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.api_key_env}")

        # Explicit timeout so a hung request fails fast into our retry loop
        # instead of blocking on the SDK's very long default (600s).
        client = OpenAI(api_key=api_key, base_url=self.base_url, timeout=30.0, max_retries=0)
        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

        # Free-tier / shared endpoints occasionally return transient 5xx or
        # connection errors. Retry a few times with backoff before failing
        # the case as a provider_error.
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                resp = client.chat.completions.create(**kwargs)
                break
            except (APIStatusError, APIConnectionError) as exc:
                is_retryable = isinstance(exc, APIConnectionError) or getattr(exc, "status_code", 0) in (429, 500, 502, 503, 504)
                if not is_retryable or attempt == max_attempts:
                    raise
                time.sleep(2 ** attempt)
        msg = resp.choices[0].message
        calls: list[ToolCall] = []
        for call in msg.tool_calls or []:
            args = json.loads(call.function.arguments or "{}")
            calls.append(ToolCall(name=call.function.name, args=args))
        return ModelResponse(text=msg.content, tool_calls=calls, raw=resp)
