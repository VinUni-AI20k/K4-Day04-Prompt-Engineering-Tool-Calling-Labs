from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err


NODES_FILE = ROOT / "helpdesk_data" / "network_nodes.json"
DANGEROUS_CHARS_PATTERN = re.compile(r"[;&|`$<>\r\n]")
VALID_CHECK_TYPES = {"all", "ping", "packet_loss", "dns", "gateway"}


def diagnose_network(target: str = "office_hanoi", check_type: str = "all") -> dict[str, Any]:
    """Kiểm tra chẩn đoán mạng nội bộ và các điểm kết nối chi nhánh."""
    try:
        if not isinstance(target, str):
            return {"tool": "diagnose_network", "error": "invalid_target_type"}
        if not isinstance(check_type, str):
            return {"tool": "diagnose_network", "error": "invalid_check_type"}

        cleaned_target = target.strip().lower()
        cleaned_check = check_type.strip().lower()

        # Guardrail: Chặn command injection và ký tự đặc biệt nguy hiểm
        if DANGEROUS_CHARS_PATTERN.search(cleaned_target) or DANGEROUS_CHARS_PATTERN.search(cleaned_check):
            return {
                "tool": "diagnose_network",
                "error": "security_violation",
                "message": "Command injection characters detected. Only alphanumeric target names are allowed.",
            }

        if cleaned_check not in VALID_CHECK_TYPES:
            return {
                "tool": "diagnose_network",
                "error": "invalid_check_type",
                "supported_check_types": sorted(VALID_CHECK_TYPES),
            }

        data = json.loads(NODES_FILE.read_text(encoding="utf-8"))
        node = next((item for item in data["nodes"] if item["target"] == cleaned_target), None)

        if node is None:
            return {
                "tool": "diagnose_network",
                "target": cleaned_target,
                "error": "target_not_found",
                "available_targets": sorted(item["target"] for item in data["nodes"]),
            }

        result_metrics: dict[str, Any] = {}
        if cleaned_check in {"all", "ping"}:
            result_metrics["ping_ms"] = node["ping_ms"]
        if cleaned_check in {"all", "packet_loss"}:
            result_metrics["packet_loss_pct"] = node["packet_loss_pct"]
        if cleaned_check in {"all", "dns"}:
            result_metrics["dns_status"] = node["dns_status"]
        if cleaned_check in {"all", "gateway"}:
            result_metrics["gateway_status"] = node["gateway_status"]
            result_metrics["bandwidth_usage_pct"] = node.get("bandwidth_usage_pct")

        return {
            "tool": "diagnose_network",
            "target": cleaned_target,
            "node_name": node["node_name"],
            "location": node["location"],
            "ip_address": node["ip_address"],
            "check_type": cleaned_check,
            "overall_status": node["status"],
            "metrics": result_metrics,
            "notes": node["notes"],
            "snapshot_at": data["snapshot_at"],
        }
    except Exception as exc:
        return err("diagnose_network", exc)
