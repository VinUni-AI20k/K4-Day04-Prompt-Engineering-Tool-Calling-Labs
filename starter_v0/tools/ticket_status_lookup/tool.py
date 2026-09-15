from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err


TICKET_DIR = ROOT / "tickets"
TICKET_ID_PATTERN = re.compile(r"^LAB-[0-9A-F]{8}$", re.IGNORECASE)


def ticket_status_lookup(ticket_id: str = "") -> dict[str, Any]:
    if not isinstance(ticket_id, str):
        return {"tool": "ticket_status_lookup", "error": "invalid_ticket_id_type"}

    normalized_id = ticket_id.strip().upper()
    if not TICKET_ID_PATTERN.fullmatch(normalized_id):
        return {"tool": "ticket_status_lookup", "error": "invalid_ticket_id"}

    path = TICKET_DIR / f"{normalized_id}.json"
    if not path.is_file():
        return {
            "tool": "ticket_status_lookup",
            "ticket_id": normalized_id,
            "error": "ticket_not_found",
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return {
            "tool": "ticket_status_lookup",
            "ticket_id": normalized_id,
            "status": payload.get("status", "open"),
            "summary": payload.get("summary", ""),
            "priority": payload.get("priority", "medium"),
            "asset_id": payload.get("asset_id"),
            "created_at": payload.get("created_at"),
        }
    except Exception as exc:
        return err("ticket_status_lookup", exc)
