from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from providers.base import Provider, ToolCall
from tools import TOOL_FUNCTIONS
from tools._shared import SENSITIVE_VALUE, external_identifier_smuggling, has_explicit_confirmation, latest_user_text


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
        results: list[dict[str, Any]] = []
        safe_calls: list[ToolCall] = []
        current_text = latest_user_text(user_messages)
        for call in response.tool_calls:
            if call.name == "create_ticket":
                summary = str(call.args.get("summary") or "")
                if SENSITIVE_VALUE.search(summary):
                    continue
                if not has_explicit_confirmation(current_text):
                    call = ToolCall(
                        name="clarify",
                        args={"question": "Bạn có xác nhận tạo ticket với payload hiện tại không?", "response_type": "yes_no"},
                    )
            elif call.name == "search_device_info" and external_identifier_smuggling(current_text):
                call = ToolCall(
                    name="clarify",
                    args={"question": "Vui lòng bỏ asset ID hoặc employee ID khỏi yêu cầu tìm kiếm web.", "response_type": "text"},
                )
            safe_calls.append(call)

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
        return AgentRun(text=response.text, tool_calls=safe_calls, tool_results=results)
