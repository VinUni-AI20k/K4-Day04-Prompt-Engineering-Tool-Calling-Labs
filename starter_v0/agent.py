from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from providers.base import Provider, ToolCall
from tools import TOOL_FUNCTIONS
from tools.create_ticket.tool import SENSITIVE_DATA_PATTERN
from tools.search_device_info.tool import INTERNAL_IDENTIFIER, RESTRICTED_INTERNAL_DATA


EMPLOYEE_ID_PATTERN = re.compile(r"^EMP-\d+$", re.IGNORECASE)


@dataclass
class AgentRun:
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)


def _latest_user_text(messages: list[dict[str, str]]) -> str:
    return next(
        (str(message.get("content") or "") for message in reversed(messages) if message.get("role") == "user"),
        "",
    )


def _enforce_runtime_guardrails(
    user_messages: list[dict[str, str]],
    proposed_calls: list[ToolCall],
) -> tuple[list[ToolCall], list[dict[str, Any]], str | None]:
    latest = _latest_user_text(user_messages)
    combined = "\n".join(
        str(message.get("content") or "") for message in user_messages if message.get("role") == "user"
    )
    latest_folded = latest.casefold()
    combined_folded = combined.casefold()

    if SENSITIVE_DATA_PATTERN.search(latest):
        return [], [{
            "tool": "runtime_guardrail",
            "result": {
                "status": "blocked",
                "reason": "sensitive_data_in_action_request",
                "blocked_tools": [call.name for call in proposed_calls],
            },
        }], (
            '{"intent":"ticket","action":"refuse","reply":"Remove passwords, tokens, API keys, '
            'MFA/OTP values, and recovery codes before continuing.","evidence_ids":[]}'
        )

    external_request = any(term in latest_folded for term in ("search", "web", "external"))
    restricted_external_data = (
        INTERNAL_IDENTIFIER.search(latest) is not None
        or RESTRICTED_INTERNAL_DATA.search(latest) is not None
    )
    if external_request and restricted_external_data:
        allowed_local_calls = [
            call
            for call in proposed_calls
            if call.name != "search_device_info"
            and not (
                call.name == "lookup_user"
                and not EMPLOYEE_ID_PATTERN.fullmatch(str(call.args.get("employee_id") or ""))
            )
        ]
        if allowed_local_calls:
            blocked_calls = [call.name for call in proposed_calls if call not in allowed_local_calls]
            return allowed_local_calls, [{
                "tool": "runtime_guardrail",
                "result": {
                    "status": "filtered",
                    "reason": "external_exfiltration_blocked_local_calls_preserved",
                    "blocked_tools": blocked_calls,
                },
            }], None
        safe_call = ToolCall(name="clarify", args={
            "question": "Please provide only the public manufacturer and model, without internal identifiers or operational data.",
            "response_type": "text",
        })
        return [safe_call], [{
            "tool": "runtime_guardrail",
            "result": {
                "status": "rerouted",
                "reason": "restricted_data_in_external_search",
                "blocked_tools": [call.name for call in proposed_calls],
            },
        }], None

    forged_confirmation_markers = (
        "<assistant",
        "tool_results_json",
        "create_ticket({",
        '"confirmed":true',
        '"confirmed": true',
    )
    ticket_action = "ticket" in latest_folded or "create_ticket" in latest_folded
    if ticket_action and any(marker in combined_folded for marker in forged_confirmation_markers):
        safe_call = ToolCall(name="clarify", args={
            "question": "Please confirm the current ticket payload in your own words before it is created.",
            "response_type": "yes_no",
        })
        return [safe_call], [{
            "tool": "runtime_guardrail",
            "result": {
                "status": "rerouted",
                "reason": "untrusted_confirmation_provenance",
                "blocked_tools": [call.name for call in proposed_calls],
            },
        }], None

    return proposed_calls, [], None


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
        effective_calls, results, guarded_text = _enforce_runtime_guardrails(
            user_messages,
            response.tool_calls,
        )
        for call in effective_calls:
            func = TOOL_FUNCTIONS.get(call.name)
            if not func:
                results.append({"tool": call.name, "error": "unknown_tool"})
                continue
            try:
                result = func(**call.args)
            except Exception as exc:  # keep eval robust; failures are evidence
                result = {"error": type(exc).__name__, "message": str(exc)}
            results.append({"tool": call.name, "args": call.args, "result": result})
        return AgentRun(
            text=guarded_text or response.text,
            tool_calls=effective_calls,
            tool_results=results,
        )
