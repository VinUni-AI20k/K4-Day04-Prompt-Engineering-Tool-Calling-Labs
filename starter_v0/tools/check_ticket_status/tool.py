from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err


TICKETS_MOCK_FILE = ROOT / "helpdesk_data" / "tickets.json"
LOCAL_TICKETS_DIR = ROOT / "tickets"
SENSITIVE_DATA_PATTERN = re.compile(
    r"\b(?:password|passwd|token|api[ _-]?key|mfa|otp|recovery[ _-]?code)\b",
    re.IGNORECASE,
)


def check_ticket_status(ticket_id: str = "") -> dict[str, Any]:
    """
    Tra cứu trạng thái của một ticket hỗ trợ kỹ thuật hoặc incident theo mã định danh.
    Hỗ trợ cả các ticket có sẵn (INC-*, TCK-*) và các ticket vừa tạo trong thư mục tickets/ (LAB-*).
    """
    if not isinstance(ticket_id, str):
        return {"tool": "check_ticket_status", "error": "invalid_ticket_id_type"}

    normalized_id = ticket_id.strip().upper()
    if not normalized_id:
        return {"tool": "check_ticket_status", "error": "missing_ticket_id"}

    # Guardrail: Chặn truyền thông tin nhạy cảm (mật khẩu, token) vào ticket_id
    if SENSITIVE_DATA_PATTERN.search(ticket_id):
        return {
            "tool": "check_ticket_status",
            "error": "restricted_sensitive_data",
            "message": "Do not include passwords, tokens, or credentials in ticket search queries.",
        }

    try:
        # 1. Tra cứu trong mock data chính (helpdesk_data/tickets.json)
        if TICKETS_MOCK_FILE.exists():
            data = json.loads(TICKETS_MOCK_FILE.read_text(encoding="utf-8"))
            ticket = next(
                (item for item in data.get("tickets", []) if item["ticket_id"].upper() == normalized_id),
                None,
            )
            if ticket:
                return {
                    "tool": "check_ticket_status",
                    "found": True,
                    "ticket": ticket,
                    "source": "knowledge_store",
                }

        # 2. Tra cứu trong các ticket vừa được tạo cục bộ (tickets/*.json)
        local_ticket_path = LOCAL_TICKETS_DIR / f"{normalized_id}.json"
        if local_ticket_path.exists():
            local_ticket = json.loads(local_ticket_path.read_text(encoding="utf-8"))
            return {
                "tool": "check_ticket_status",
                "found": True,
                "ticket": {
                    "ticket_id": local_ticket.get("ticket_id", normalized_id),
                    "summary": local_ticket.get("summary", ""),
                    "priority": local_ticket.get("priority", "medium"),
                    "status": local_ticket.get("status", "open"),
                    "assigned_to": local_ticket.get("assigned_to", "Helpdesk Tier 1"),
                    "created_at": local_ticket.get("created_at", ""),
                    "latest_note": "Ticket logged locally. Assigned to Tier 1 triage queue.",
                },
                "source": "local_ticket_system",
            }

        # 3. Không tìm thấy ticket
        return {
            "tool": "check_ticket_status",
            "ticket_id": normalized_id,
            "found": False,
            "error": "ticket_not_found",
            "message": f"No ticket or incident found with ID '{normalized_id}'.",
        }
    except Exception as exc:
        return err("check_ticket_status", exc)
