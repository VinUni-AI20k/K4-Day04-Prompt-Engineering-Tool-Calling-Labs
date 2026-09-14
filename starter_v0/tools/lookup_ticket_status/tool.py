from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


TICKETS_DIR = ROOT / "tickets"
MOCK_TICKETS_FILE = ROOT / "helpdesk_data" / "mock_tickets.json"


def lookup_ticket_status(ticket_id: str = "") -> dict[str, Any]:
    """
    Tra cứu thông tin chi tiết và tiến độ xử lý của một ticket hỗ trợ IT theo ticket_id.
    Hỗ trợ cả các ticket có sẵn trong mock database lẫn các ticket vừa được tạo trong tickets/.
    """
    try:
        normalized_id = (ticket_id or "").strip().upper()
        if not normalized_id:
            return {
                "tool": "lookup_ticket_status",
                "error": "missing_ticket_id",
                "message": "Please provide a valid ticket ID (e.g. INC-1042 or LAB-xxxxxxxx).",
            }

        # 1. Kiểm tra trong thư mục tickets/ (các ticket vừa được sinh ra bởi create_ticket)
        if TICKETS_DIR.exists():
            local_ticket_path = TICKETS_DIR / f"{normalized_id}.json"
            if local_ticket_path.exists():
                data = json.loads(local_ticket_path.read_text(encoding="utf-8"))
                return {
                    "tool": "lookup_ticket_status",
                    "ticket_id": data.get("ticket_id", normalized_id),
                    "status": "open",
                    "summary": data.get("summary", ""),
                    "priority": data.get("priority", "medium"),
                    "asset_id": data.get("asset_id"),
                    "requester_id": data.get("requester_id", "current_user"),
                    "assigned_to": "Tier-1 Helpdesk Queue (Pending Triage)",
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("created_at"),
                    "resolution_notes": "Ticket recently created and awaiting triage by an IT technician.",
                    "source": "local_ticket_store",
                }

        # 2. Kiểm tra trong file mock_tickets.json
        if MOCK_TICKETS_FILE.exists():
            data = json.loads(MOCK_TICKETS_FILE.read_text(encoding="utf-8"))
            for ticket in data.get("tickets", []):
                if ticket.get("ticket_id", "").strip().upper() == normalized_id:
                    return {
                        "tool": "lookup_ticket_status",
                        **ticket,
                        "source": "helpdesk_mock_database",
                    }

        # 3. Không tìm thấy ticket
        available_samples = []
        if MOCK_TICKETS_FILE.exists():
            sample_data = json.loads(MOCK_TICKETS_FILE.read_text(encoding="utf-8"))
            available_samples = [t.get("ticket_id") for t in sample_data.get("tickets", []) if t.get("ticket_id")]

        return {
            "tool": "lookup_ticket_status",
            "ticket_id": normalized_id,
            "error": "ticket_not_found",
            "message": f"Ticket '{normalized_id}' not found in IT helpdesk system.",
            "available_samples": available_samples[:5],
        }

    except Exception as exc:
        return err("lookup_ticket_status", exc)
