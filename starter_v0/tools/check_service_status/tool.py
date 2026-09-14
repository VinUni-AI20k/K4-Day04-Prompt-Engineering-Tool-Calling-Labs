from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


STATUS_FILE = ROOT / "helpdesk_data" / "service_status.json"


def check_service_status(service: str = "", environment: str = "production") -> dict[str, Any]:
    try:
        data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        service_key = (service or "").strip().lower()
        environment_key = (environment or "production").strip().lower()
        for item in data["services"]:
            if item["service"] == service_key and item["environment"] == environment_key:
                return {"tool": "check_service_status", **item, "checked_at": data["snapshot_at"]}
        return {
            "tool": "check_service_status",
            "service": service_key,
            "environment": environment_key,
            "error": "not_found",
            "available_services": sorted({item["service"] for item in data["services"]}),
        }
    except Exception as exc:
        return err("check_service_status", exc)
SCHEMA = {
    "name": "check_service_status",
    "description": "Đọc trang trạng thái giả lập xác định cho một dịch vụ dùng chung và môi trường cụ thể. Công cụ này không dùng để chẩn đoán thiết bị cá nhân của nhân viên.",
    "parameters": {
        "type": "object",
        "properties": {
            "service": {
                "type": "string",
                "description": "Tên của dịch vụ cần kiểm tra trạng thái."
            },
            "environment": {
                "type": "string",
                "description": "Môi trường của dịch vụ cần kiểm tra (ví dụ: production, staging). Mặc định là 'production'."
            }
        },
        "required": ["service"]
    }
}