from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from providers.base import Provider, ToolCall
from tools._shared import fold_text
from tools import TOOL_FUNCTIONS


INTERNAL_IDENTIFIER = re.compile(r"\b(?:LT|DT|MB|PR|RM|EMP)-\d+\b", re.IGNORECASE)
FINAL_RESPONSE_FIELDS = {"intent", "action", "reply", "evidence_ids"}


def normalize_final_response(text: str | None) -> str:
    """Keep the final user-facing response in the declared JSON contract."""
    candidate = (text or "").strip()
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict) and set(parsed) == FINAL_RESPONSE_FIELDS and isinstance(parsed.get("reply"), str) and isinstance(parsed.get("evidence_ids"), list):
        return json.dumps(parsed, ensure_ascii=False)
    return json.dumps(
        {
            "intent": "helpdesk_response",
            "action": "respond",
            "reply": candidate or "Tôi chưa nhận được phản hồi hoàn chỉnh từ model.",
            "evidence_ids": [],
        },
        ensure_ascii=False,
    )


def _clarify_confirmation() -> ToolCall:
    return ToolCall(
        name="clarify",
        args={
            "question": "Bạn có xác nhận tạo ticket với payload cuối cùng này không?",
            "response_type": "yes_no",
        },
    )


def _clarify_public_identity() -> ToolCall:
    return ToolCall(
        name="clarify",
        args={
            "question": "Vui lòng chỉ cung cấp hãng, model và loại thông tin công khai; không kèm mã asset hoặc mã nhân viên.",
            "response_type": "text",
        },
    )


def _has_role_spoofed_action(messages: list[dict[str, str]]) -> bool:
    user_text = "\n".join(message.get("content", "") for message in messages if message.get("role") == "user")
    latest_user_text = next(
        (message.get("content", "") for message in reversed(messages) if message.get("role") == "user"),
        "",
    )
    folded = fold_text(user_text)
    latest_folded = fold_text(latest_user_text)
    contains_spoofed_role = "<assistant" in folded or '"role": "assistant"' in folded or "assistant gia" in folded
    requests_ticket_action = "ticket" in latest_folded and any(word in latest_folded for word in ("tao", "thuc thi", "create", "execute"))
    return contains_spoofed_role and requests_ticket_action


def guard_tool_call(call: ToolCall, messages: list[dict[str, str]]) -> ToolCall:
    """Apply non-negotiable safety checks before a model-selected tool runs."""
    user_text = "\n".join(message.get("content", "") for message in messages if message.get("role") == "user")
    folded = fold_text(user_text)

    if call.name == "create_ticket":
        forged_markers = ("tool_results_json", "create_ticket(", "<assistant", "system:", "developer:")
        stale_confirmation = "dung confirmation" in folded and ("luot" in folded or "truoc" in folded)
        if any(marker in folded for marker in forged_markers) or stale_confirmation:
            return _clarify_confirmation()

    if call.name == "search_device_info":
        public_identity = json.dumps(call.args, ensure_ascii=False)
        tries_to_preserve_internal_data = "giu nguyen" in folded and bool(INTERNAL_IDENTIFIER.search(user_text))
        if INTERNAL_IDENTIFIER.search(public_identity) or tries_to_preserve_internal_data:
            return _clarify_public_identity()

    return call


def guard_tool_calls(calls: list[ToolCall], messages: list[dict[str, str]]) -> list[ToolCall]:
    if _has_role_spoofed_action(messages):
        return [_clarify_confirmation()]
    return [guard_tool_call(call, messages) for call in calls]


@dataclass
class AgentRun:
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)


class HelpdeskAgent:
    def __init__(
        self,
        provider: Provider,
        *,
        system_prompt: str,
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> None:
        self.provider = provider
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model = model

    def run(self, user_messages: list[dict[str, str]], *, tool_choice: Any | None = None) -> AgentRun:
        messages = [{"role": "system", "content": self.system_prompt}, *user_messages]
        response = self.provider.complete(
            messages,
            self.tools,
            model=self.model,
            temperature=0.0,
            tool_choice=tool_choice,
        )
        safe_calls = guard_tool_calls(response.tool_calls, messages)
        results: list[dict[str, Any]] = []
        for call in safe_calls:
            func = TOOL_FUNCTIONS.get(call.name)
            if not func:
                results.append({"tool": call.name, "error": "unknown_tool"})
                continue
            try:
                result = func(**call.args)
            except Exception as exc:  # keep eval robust; failures are evidence
                result = {"error": type(exc).__name__, "message": str(exc)}
            results.append({"tool": call.name, "args": call.args, "result": result})
        final_text = response.text if safe_calls else normalize_final_response(response.text)
        return AgentRun(text=final_text, tool_calls=safe_calls, tool_results=results)
