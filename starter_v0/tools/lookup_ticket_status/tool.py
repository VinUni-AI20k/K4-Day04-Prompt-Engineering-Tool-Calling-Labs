from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err


TICKET_STATUS_FILE = ROOT / "helpdesk_data" / "ticket_statuses.json"
TICKET_ID_PATTERN = re.compile(r"^LAB-[A-F0-9]{8}$", re.IGNORECASE)
PUBLIC_FIELDS = ("ticket_id", "status", "priority", "asset_id", "updated_at", "summary")


def lookup_ticket_status(ticket_id: str = "") -> dict[str, Any]:
    """Return one anonymized mock ticket status without touching generated tickets."""
    if not isinstance(ticket_id, str):
        return {"tool": "lookup_ticket_status", "error": "invalid_ticket_id_type"}

    normalized_id = ticket_id.strip().upper()
    if not TICKET_ID_PATTERN.fullmatch(normalized_id):
        return {
            "tool": "lookup_ticket_status",
            "error": "invalid_ticket_id",
            "message": "ticket_id must use the format LAB-XXXXXXXX.",
        }

    try:
        data = json.loads(TICKET_STATUS_FILE.read_text(encoding="utf-8"))
        for ticket in data.get("tickets", []):
            if ticket.get("ticket_id", "").upper() == normalized_id:
                return {"tool": "lookup_ticket_status", **{key: ticket.get(key) for key in PUBLIC_FIELDS}}
        return {
            "tool": "lookup_ticket_status",
            "ticket_id": normalized_id,
            "error": "ticket_not_found",
        }
    except Exception as exc:
        return err("lookup_ticket_status", exc)
