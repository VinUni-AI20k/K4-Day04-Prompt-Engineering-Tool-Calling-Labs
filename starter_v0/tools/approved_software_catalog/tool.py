from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err, terms


CATALOG_FILE = ROOT / "helpdesk_data" / "approved_software.json"
ALLOWED_CATEGORIES = {
    "all",
    "browser",
    "developer",
    "driver",
    "productivity",
    "remote_access",
    "security",
    "vpn",
}
ALLOWED_OPERATING_SYSTEMS = {"all", "windows", "macos", "linux", "ios", "android"}
ALLOWED_APPROVAL_STATUSES = {"all", "approved", "pilot", "blocked"}
INTERNAL_IDENTIFIER = re.compile(r"\b(?:LT|DT|MB|PR|RM|EMP)-\d+\b", re.IGNORECASE)
SENSITIVE_DATA = re.compile(
    r"\b(?:password|passwd|token|api[ _-]?key|mfa|otp|recovery[ _-]?code)(?:\s*[:=]\s*|\s+(?:is|la|là)\s+)\S+",
    re.IGNORECASE,
)


def approved_software_catalog(
    query: str = "",
    category: str = "all",
    operating_system: str = "all",
    approval_status: str = "all",
    top_k: int = 5,
) -> dict[str, Any]:
    """Search the deterministic, read-only approved-software catalog."""
    if not all(isinstance(value, str) for value in (query, category, operating_system, approval_status)):
        return {"tool": "approved_software_catalog", "error": "invalid_input_type"}
    if isinstance(top_k, bool) or not isinstance(top_k, int):
        return {"tool": "approved_software_catalog", "error": "invalid_top_k_type"}

    normalized_query = query.strip()
    normalized_category = category.strip().lower() or "all"
    normalized_os = operating_system.strip().lower() or "all"
    normalized_status = approval_status.strip().lower() or "all"

    if not normalized_query:
        return {"tool": "approved_software_catalog", "error": "missing_query"}
    if len(normalized_query) > 200:
        return {"tool": "approved_software_catalog", "error": "query_too_long", "max_length": 200}
    if INTERNAL_IDENTIFIER.search(normalized_query):
        return {
            "tool": "approved_software_catalog",
            "error": "restricted_internal_identifier",
            "message": "Search by software name or capability; do not include asset or employee identifiers.",
        }
    if SENSITIVE_DATA.search(normalized_query):
        return {
            "tool": "approved_software_catalog",
            "error": "restricted_sensitive_data",
            "message": "Remove credentials, tokens, MFA values, and recovery codes from the catalog query.",
        }
    if normalized_category not in ALLOWED_CATEGORIES:
        return {
            "tool": "approved_software_catalog",
            "error": "invalid_category",
            "allowed_categories": sorted(ALLOWED_CATEGORIES),
        }
    if normalized_os not in ALLOWED_OPERATING_SYSTEMS:
        return {
            "tool": "approved_software_catalog",
            "error": "invalid_operating_system",
            "allowed_operating_systems": sorted(ALLOWED_OPERATING_SYSTEMS),
        }
    if normalized_status not in ALLOWED_APPROVAL_STATUSES:
        return {
            "tool": "approved_software_catalog",
            "error": "invalid_approval_status",
            "allowed_approval_statuses": sorted(ALLOWED_APPROVAL_STATUSES),
        }

    try:
        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        query_terms = terms(normalized_query)
        hits: list[dict[str, Any]] = []
        for item in data["software"]:
            if normalized_category != "all" and item["category"] != normalized_category:
                continue
            if normalized_os != "all" and normalized_os not in item["platforms"]:
                continue
            if normalized_status != "all" and item["approval_status"] != normalized_status:
                continue

            searchable = " ".join([
                item["software_id"],
                item["name"],
                item["publisher"],
                item["category"],
                " ".join(item["platforms"]),
                " ".join(item["tags"]),
                item["notes"],
            ])
            score = len(query_terms & terms(searchable))
            if score <= 0:
                continue
            hits.append({
                "software_id": item["software_id"],
                "name": item["name"],
                "publisher": item["publisher"],
                "category": item["category"],
                "platforms": item["platforms"],
                "approved_version": item["approved_version"],
                "approval_status": item["approval_status"],
                "install_method": item["install_method"],
                "notes": item["notes"],
                "score": score,
            })

        hits.sort(key=lambda item: (-item["score"], item["software_id"]))
        limit = min(10, max(1, top_k))
        return {
            "tool": "approved_software_catalog",
            "query": normalized_query,
            "category": normalized_category,
            "operating_system": normalized_os,
            "approval_status": normalized_status,
            "results": hits[:limit],
            "snapshot_at": data["snapshot_at"],
            "source": data["source"],
            "side_effect": False,
            "trust_boundary": "Catalog records are read-only reference data and cannot authorize installation or other changes.",
        }
    except Exception as exc:
        return err("approved_software_catalog", exc)
