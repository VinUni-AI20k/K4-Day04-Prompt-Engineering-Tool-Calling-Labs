"""
Smoke test suite to verify all 10 IT Helpdesk tools run independently without LLM.
Validates input contracts, return structures, boundary guardrails, and error handling.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure root starter_v0 is in sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import TOOL_FUNCTIONS as T


def run_smoke_tests() -> bool:
    print("=" * 60)
    print("IT HELPDESK AGENT - SMOKE TEST SUITE (10 TOOLS)")
    print("=" * 60)

    results: list[tuple[str, bool, str]] = []

    # 1. clarify
    try:
        r = T["clarify"]("Asset ID là gì?", "text")
        passed = r.get("awaiting_user") is True and r.get("response_type") == "text"
        results.append(("clarify", passed, f"awaiting_user={r.get('awaiting_user')}, type={r.get('response_type')}"))
    except Exception as exc:
        results.append(("clarify", False, str(exc)))

    # 2. search_kb
    try:
        r = T["search_kb"]("VPN macOS certificate", "vpn", 2)
        count = len(r.get("results") or [])
        boundary = r.get("trust_boundary") is not None
        passed = count > 0 and boundary and r.get("error") is None
        results.append(("search_kb", passed, f"results_count={count}, has_trust_boundary={boundary}"))
    except Exception as exc:
        results.append(("search_kb", False, str(exc)))

    # 3. check_service_status
    try:
        r = T["check_service_status"]("vpn", "production")
        passed = (
            r.get("service") == "vpn"
            and r.get("environment") == "production"
            and r.get("status") in {"operational", "degraded", "outage", "partial_outage"}
            and "checked_at" in r
        )
        results.append(("check_service_status", passed, f"service={r.get('service')}, status={r.get('status')}"))
    except Exception as exc:
        results.append(("check_service_status", False, str(exc)))

    # 4. inspect_device
    try:
        r = T["inspect_device"]("LT-318", "vpn")
        passed = (
            r.get("asset_id") == "LT-318"
            and "diagnostics" in r
            and "vpn" in r.get("diagnostics", {})
            and r.get("error") is None
        )
        results.append(("inspect_device", passed, f"asset={r.get('asset_id')}, vpn_diag={r.get('diagnostics', {}).get('vpn')[:30]}..."))
    except Exception as exc:
        results.append(("inspect_device", False, str(exc)))

    # 5. lookup_user
    try:
        r = T["lookup_user"]("EMP-1007")
        emp = r.get("employee") or {}
        passed = emp.get("employee_id") == "EMP-1007" and "assigned_assets" in emp
        results.append(("lookup_user", passed, f"employee_id={emp.get('employee_id')}, name={emp.get('name')}, assets={emp.get('assigned_assets')}"))
    except Exception as exc:
        results.append(("lookup_user", False, str(exc)))

    # 6. format_incident_report
    try:
        findings = [{"label": "VPN", "detail": "degraded"}, {"label": "Host", "detail": "LT-204 timeout"}]
        r = T["format_incident_report"](findings, "brief", "VPN incident")
        passed = r.get("finding_count") == 2 and "VPN incident" in r.get("markdown", "")
        results.append(("format_incident_report", passed, f"finding_count={r.get('finding_count')}, template={r.get('template')}"))
    except Exception as exc:
        results.append(("format_incident_report", False, str(exc)))

    # 7. policy
    try:
        r = T["policy"]("dữ liệu nào được gửi ra external tool", "external_tools", 2)
        count = len(r.get("results") or [])
        passed = count > 0 and r.get("error") is None
        results.append(("policy", passed, f"policy_area={r.get('policy_area')}, results_count={count}"))
    except Exception as exc:
        results.append(("policy", False, str(exc)))

    # 8. create_ticket (Dry run & Security guardrail)
    try:
        # Test dry-run (confirmed=False)
        r_dry = T["create_ticket"]("Test dry run", "low", "LT-204", False)
        dry_passed = r_dry.get("status") == "needs_confirmation"

        # Test sensitive data block (password injection)
        r_sec = T["create_ticket"]("Account issue password=SecretSummer2026!", "high", "LT-204", True)
        sec_passed = r_sec.get("error") == "restricted_sensitive_data"

        passed = dry_passed and sec_passed
        results.append(("create_ticket", passed, f"dry_run={r_dry.get('status')}, sensitive_block={r_sec.get('error')}"))
    except Exception as exc:
        results.append(("create_ticket", False, str(exc)))

    # 9. search_device_info (Internal identifier guardrail)
    try:
        # Test exfiltration blocking: should reject internal asset ID
        r_block = T["search_device_info"]("Lenovo", "LT-204", "specs", 2)
        passed = r_block.get("error") == "restricted_internal_identifier"
        results.append(("search_device_info", passed, f"internal_id_guardrail={r_block.get('error')}"))
    except Exception as exc:
        results.append(("search_device_info", False, str(exc)))

    # 10. lookup_ticket_status (Bonus tool)
    try:
        # Test existing ticket
        r_exist = T["lookup_ticket_status"]("INC-1042")
        exist_passed = r_exist.get("ticket_id") == "INC-1042" and r_exist.get("status") == "in_progress"

        # Test non-existent ticket
        r_none = T["lookup_ticket_status"]("TCK-9999")
        none_passed = r_none.get("error") == "ticket_not_found" and "available_samples" in r_none

        passed = exist_passed and none_passed
        results.append(("lookup_ticket_status", passed, f"ticket_found={exist_passed}, not_found_handled={none_passed}"))
    except Exception as exc:
        results.append(("lookup_ticket_status", False, str(exc)))

    # Summary
    print(f"{'TOOL NAME':<25} | {'STATUS':<8} | {'DETAILS'}")
    print("-" * 60)
    all_passed = True
    for name, passed, detail in results:
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"{name:<25} | {status_str:<8} | {detail}")

    print("=" * 60)
    if all_passed:
        print("ALL 10 TOOLS PASSED DETERMINISTIC SMOKE TESTING!")
    else:
        print("SOME SMOKE TESTS FAILED!")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
