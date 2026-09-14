"""Deterministic Module 4 checks for side effects, injection, and data boundaries."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.create_ticket import tool as ticket_tool
from tools.create_ticket.tool import create_ticket
from tools.policy.tool import search_company_policy
from tools.search_device_info import tool as device_tool
from tools.search_device_info.tool import search_device_info
from tools.search_kb.tool import search_kb


def check_ticket_guardrails() -> None:
    with tempfile.TemporaryDirectory() as directory:
        with patch.object(ticket_tool, "TICKET_DIR", Path(directory)):
            pending = create_ticket("VPN issue", confirmed=False)
            assert pending["status"] == "needs_confirmation"
            assert not list(Path(directory).glob("*.json"))
            blocked = create_ticket("Password=Summer2026!", confirmed=True)
            assert blocked["error"] == "restricted_sensitive_data"
            blocked_otp = create_ticket("OTP 123456", confirmed=True)
            assert blocked_otp["error"] == "restricted_sensitive_data"
            blocked_mfa = create_ticket("MFA code: 123456", confirmed=True)
            assert blocked_mfa["error"] == "restricted_sensitive_data"
            strict_bool = create_ticket("VPN issue", confirmed=1)
            assert strict_bool["status"] == "needs_confirmation"
            assert not list(Path(directory).glob("*.json"))


def check_retrieval_injection() -> None:
    kb = search_kb("print queue troubleshooting safety sample", category="printing")
    assert kb["results"]
    assert all("ignore previous" not in item["content"].casefold() for item in kb["results"])
    assert any(item["untrusted_text"] for item in kb["results"])

    policy = search_company_policy("incident response critical", policy_area="incident_response")
    assert policy["results"]
    assert all("ignore" not in item["facts"].casefold() for item in policy["results"])
    assert any(item["untrusted_text"] for item in policy["results"])


def check_external_boundary() -> None:
    blocked_inputs = [
        {"manufacturer": "Lenovo", "model": "ThinkPad T14 LT-204", "query_type": "specs"},
        {"manufacturer": "Lenovo", "model": "ThinkPad T14, assigned user Alice, location Hanoi", "query_type": "support"},
    ]
    for kwargs in blocked_inputs:
        result = search_device_info(**kwargs)
        assert result["error"] in {"restricted_internal_identifier", "restricted_internal_data"}

    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"results": []}

    captured: dict[str, object] = {}

    def fake_post(url: str, *, json: dict[str, object], headers: dict[str, str], timeout: int) -> Response:
        captured.update(json)
        return Response()

    with patch.dict(os.environ, {"TAVILY_API_KEY": "test-only"}), patch.object(device_tool.requests, "post", fake_post):
        result = search_device_info("Lenovo", "ThinkPad T14 Gen 4", "drivers")
    assert result["tool"] == "search_device_info"
    query = str(captured["query"]).casefold()
    assert not any(token in query for token in ("lt-", "emp-", "serial", "hostname", "location", "diagnostic"))


def main() -> None:
    check_ticket_guardrails()
    check_retrieval_injection()
    check_external_boundary()
    print("guardrail checks: PASS (ticket side effect, retrieval injection, external data boundary)")


if __name__ == "__main__":
    main()
