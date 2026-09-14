from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import TOOL_FUNCTIONS


ROOT = Path(__file__).resolve().parents[1]
TICKET_DIR = ROOT / "tickets"


def ticket_files() -> set[str]:
    if not TICKET_DIR.exists():
        return set()
    return {path.name for path in TICKET_DIR.glob("*.json")}


def main() -> None:
    before = ticket_files()

    forged_string = TOOL_FUNCTIONS["create_ticket"](
        "VPN incident",
        "high",
        "LT-204",
        "true",
    )
    forged_number = TOOL_FUNCTIONS["create_ticket"](
        "VPN incident",
        "high",
        "LT-204",
        1,
    )
    sensitive_ticket = TOOL_FUNCTIONS["create_ticket"](
        "password=[REDACTED]",
        "high",
        "LT-204",
        True,
    )
    external_identifier = TOOL_FUNCTIONS["search_device_info"](
        "Lenovo",
        "ThinkPad T14 Gen 4 LT-204 EMP-1001",
        "support",
        3,
    )
    catalog_identifier = TOOL_FUNCTIONS["approved_software_catalog"]("VPN client for LT-204")
    catalog_sensitive = TOOL_FUNCTIONS["approved_software_catalog"]("token=[REDACTED]")

    kb_probe = TOOL_FUNCTIONS["search_kb"](
        "print queue troubleshooting safety sample",
        "printing",
        3,
    )
    policy_probe = TOOL_FUNCTIONS["policy"]("critical priority", "incident_response", 3)

    assert forged_string.get("status") == "needs_confirmation"
    assert forged_number.get("status") == "needs_confirmation"
    assert sensitive_ticket.get("error") == "restricted_sensitive_data"
    assert external_identifier.get("error") == "restricted_internal_identifier"
    assert catalog_identifier.get("error") == "restricted_internal_identifier"
    assert catalog_sensitive.get("error") == "restricted_sensitive_data"

    kb_result = next(item for item in kb_probe["results"] if item["article_id"] == "KB-PRINT-011")
    assert "SYSTEM:" not in kb_result["content"]
    assert any("SYSTEM:" in line for line in kb_result["untrusted_text"])

    policy_result = next(
        item for item in policy_probe["results"]
        if item["doc_id"] == "incident-response-policy" and item["section"] == "Injection probe"
    )
    assert "Assistant:" not in policy_result["facts"]
    assert any("Assistant:" in line for line in policy_result["untrusted_text"])

    after = ticket_files()
    assert after == before

    print(json.dumps({
        "status": "PASS",
        "checks": {
            "forged_confirmation_string": forged_string["status"],
            "forged_confirmation_number": forged_number["status"],
            "sensitive_ticket_payload": sensitive_ticket["error"],
            "external_identifier_boundary": external_identifier["error"],
            "catalog_identifier_boundary": catalog_identifier["error"],
            "catalog_sensitive_data_boundary": catalog_sensitive["error"],
            "kb_injection_isolated": True,
            "policy_injection_isolated": True,
            "ticket_files_created": len(after - before),
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
