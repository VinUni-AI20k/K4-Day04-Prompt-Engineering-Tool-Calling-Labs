from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err, fold_text


CATALOG_FILE = ROOT / "helpdesk_data" / "software_catalog.json"
VALID_PLATFORMS = {"all", "windows", "macos", "linux"}


def check_software_catalog(software_name: str = "", platform: str = "all") -> dict[str, Any]:
    if not isinstance(software_name, str):
        return {"tool": "check_software_catalog", "error": "invalid_software_name_type"}
    wanted_name = (software_name or "").strip()
    if not wanted_name:
        return {"tool": "check_software_catalog", "error": "missing_software_name"}

    wanted_platform = (platform or "all").strip().lower()
    if wanted_platform not in VALID_PLATFORMS:
        return {
            "tool": "check_software_catalog",
            "error": "invalid_platform",
            "provided_platform": wanted_platform,
            "allowed_platforms": sorted(VALID_PLATFORMS),
        }

    try:
        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        folded_query = fold_text(wanted_name)

        matched_item: dict[str, Any] | None = None
        for item in data.get("software", []):
            item_folded = fold_text(item["name"])
            aliases = [fold_text(alias) for alias in item.get("aliases", [])]

            if (
                folded_query == item_folded
                or folded_query in aliases
                or folded_query in item_folded
                or any(folded_query in a or a in folded_query for a in aliases)
            ):
                matched_item = item
                break

        if matched_item is None:
            return {
                "tool": "check_software_catalog",
                "software_name": wanted_name,
                "error": "not_found",
                "message": f"Software '{wanted_name}' was not found in company software catalog.",
                "available_software": sorted(item["name"] for item in data.get("software", [])),
            }

        supported_platforms = matched_item.get("platforms", [])
        platform_supported = True
        if wanted_platform != "all":
            platform_supported = wanted_platform in [p.lower() for p in supported_platforms]

        return {
            "tool": "check_software_catalog",
            "software_name": matched_item["name"],
            "status": matched_item["status"],
            "category": matched_item.get("category", ""),
            "license_type": matched_item.get("license_type", ""),
            "platforms": supported_platforms,
            "platform_queried": wanted_platform,
            "platform_supported": platform_supported,
            "install_source": matched_item.get("install_source", ""),
            "notes": matched_item.get("notes", ""),
            "snapshot_at": data.get("snapshot_at"),
        }
    except Exception as exc:
        return err("check_software_catalog", exc)
