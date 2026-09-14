"""Request handling shared by the Vercel functions and the local dev server.

Both entry points call these, so validation and response shape cannot drift
between `npm run dev` on a teammate's laptop and the deployed function.
"""

from __future__ import annotations

from typing import Any

try:
    from _agent import DEFAULT_MODEL, DEFAULT_PROVIDER, LAB_ROOT, artifact_version, run_turn
except ImportError:  # imported as a package (local dev server)
    from api._agent import (  # type: ignore
        DEFAULT_MODEL,
        DEFAULT_PROVIDER,
        LAB_ROOT,
        artifact_version,
        run_turn,
    )

MAX_BODY_BYTES = 64 * 1024


def chat_response(payload: Any) -> tuple[int, dict[str, Any]]:
    if not isinstance(payload, dict):
        return 400, {"error": "invalid_payload", "message": "Expected a JSON object."}

    message = (payload.get("message") or "").strip()
    if not message:
        return 400, {"error": "missing_message", "message": "Field 'message' is required."}

    # Only well-formed turns are carried forward; anything else is dropped rather
    # than handed to the provider as a malformed message.
    history = [
        {"role": item["role"], "content": item["content"]}
        for item in (payload.get("history") or [])
        if isinstance(item, dict)
        and item.get("role") in ("user", "assistant")
        and isinstance(item.get("content"), str)
    ]

    try:
        return 200, run_turn(
            message,
            history,
            model=payload.get("model") or None,
            provider_name=payload.get("provider") or None,
        )
    except Exception as exc:  # noqa: BLE001 - rendered by the UI as a failed turn
        return 500, {"error": type(exc).__name__, "message": str(exc)}


def meta_response() -> tuple[int, dict[str, Any]]:
    try:
        return 200, {
            "ok": True,
            "artifact": artifact_version(),
            "model": DEFAULT_MODEL,
            "provider": DEFAULT_PROVIDER,
            "lab_root": str(LAB_ROOT),
        }
    except Exception as exc:  # noqa: BLE001
        return 500, {"ok": False, "error": type(exc).__name__, "message": str(exc)}
