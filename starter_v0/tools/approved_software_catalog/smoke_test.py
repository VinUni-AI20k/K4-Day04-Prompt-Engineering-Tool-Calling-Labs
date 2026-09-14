from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.approved_software_catalog.tool import approved_software_catalog


def main() -> None:
    approved = approved_software_catalog(
        "Northstar SecureConnect",
        category="vpn",
        operating_system="macos",
        approval_status="approved",
        top_k=3,
    )
    assert approved.get("error") is None
    assert [item["software_id"] for item in approved["results"]] == ["SW-VPN-001"]
    assert approved["side_effect"] is False

    incompatible = approved_software_catalog(
        "Universal Print Driver",
        category="driver",
        operating_system="macos",
        approval_status="approved",
    )
    assert incompatible["results"] == []

    internal_id = approved_software_catalog("VPN client for LT-204")
    assert internal_id.get("error") == "restricted_internal_identifier"

    sensitive = approved_software_catalog("VPN password=[REDACTED]")
    assert sensitive.get("error") == "restricted_sensitive_data"

    print(json.dumps({
        "status": "PASS",
        "approved_match": approved["results"][0]["software_id"],
        "platform_filter_results": len(incompatible["results"]),
        "internal_identifier_guardrail": internal_id["error"],
        "sensitive_data_guardrail": sensitive["error"],
        "side_effect": approved["side_effect"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
