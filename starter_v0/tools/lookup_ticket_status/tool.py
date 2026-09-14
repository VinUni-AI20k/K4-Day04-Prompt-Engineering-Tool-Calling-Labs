from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err


TICKET_DIR = ROOT / "tickets"
MOCK_TICKETS_FILE = ROOT / "helpdesk_data" / "tickets.json"
TICKET_ID_PATTERN = re.compile(r"^(?:LAB-[A-F0-9]{8}|INC-\d{3,6})$", re.IGNORECASE)
SENSITIVE_DATA_PATTERN = re.compile(
    r"\b(?:password|passwd|token|api[ _-]?key|mfa|otp|recovery[ _-]?code)(?:\s*[:=]\s*|\s+(?:is|la|là)\s+)\S+",
    re.IGNORECASE,
)


def lookup_ticket_status(ticket_id: str = "") -> dict[str, Any]:
    """Tra cứu trạng thái xử lý của một ticket hỗ trợ (từ tickets/ local hoặc mock data)."""
    try:
        if not isinstance(ticket_id, str):
            return {"tool": "lookup_ticket_status", "error": "invalid_ticket_id_type"}

        cleaned_id = (ticket_id or "").strip().upper()
        if not cleaned_id:
            return {"tool": "lookup_ticket_status", "error": "missing_ticket_id"}

        # Guardrail: Chống path traversal và định dạng mã không hợp lệ
        if not TICKET_ID_PATTERN.fullmatch(cleaned_id):
            return {
                "tool": "lookup_ticket_status",
                "ticket_id": cleaned_id,
                "error": "invalid_ticket_id_format",
                "message": "Ticket ID must match pattern 'LAB-XXXXXXXX' or 'INC-XXXX'. Path traversal is blocked.",
            }

        # 1. Kiểm tra trong thư mục tickets/ (vé vừa được tạo bởi create_ticket)
        local_ticket_path = TICKET_DIR / f"{cleaned_id}.json"
        if local_ticket_path.is_file():
            try:
                ticket_data = json.loads(local_ticket_path.read_text(encoding="utf-8"))
                # Guardrail: Che giấu nếu có dữ liệu nhạy cảm
                summary = ticket_data.get("summary", "")
                sanitized_summary = SENSITIVE_DATA_PATTERN.sub("[REDACTED_CREDENTIAL]", summary)
                return {
                    "tool": "lookup_ticket_status",
                    "ticket_id": cleaned_id,
                    "source": "local_ticket_store",
                    "status": ticket_data.get("status", "open"),
                    "priority": ticket_data.get("priority", "medium"),
                    "summary": sanitized_summary,
                    "asset_id": ticket_data.get("asset_id"),
                    "created_at": ticket_data.get("created_at"),
                    "assigned_to": "IT Helpdesk Queue",
                    "resolution_note": "Ticket đang chờ kỹ thuật viên tiếp nhận xử lý.",
                }
            except Exception:
                pass

        # 2. Kiểm tra trong mock data lịch sử helpdesk_data/tickets.json
        if MOCK_TICKETS_FILE.is_file():
            data = json.loads(MOCK_TOCKETS_TEXT := MOCK_TICKETS_FILE.read_text(encoding="utf-8"))
            for ticket in data.get("tickets", []):
                if ticket.get("ticket_id") == cleaned_id:
                    summary = ticket.get("summary", "")
                    sanitized_summary = SENSITIVE_DATA_PATTERN.sub("[REDACTED_CREDENTIAL]", summary)
                    return {
                        "tool": "lookup_ticket_status",
                        "ticket_id": cleaned_id,
                        "source": "historical_ticket_store",
                        "status": ticket.get("status"),
                        "priority": ticket.get("priority"),
                        "summary": sanitized_summary,
                        "asset_id": ticket.get("asset_id"),
                        "requester": ticket.get("requester"),
                        "assigned_to": ticket.get("assigned_to"),
                        "created_at": ticket.get("created_at"),
                        "updated_at": ticket.get("updated_at"),
                        "resolution_note": ticket.get("resolution_note"),
                    }

        return {
            "tool": "lookup_ticket_status",
            "ticket_id": cleaned_id,
            "error": "ticket_not_found",
            "message": f"Không tìm thấy ticket có mã '{cleaned_id}'.",
        }
    except Exception as exc:
        return err("lookup_ticket_status", exc)
