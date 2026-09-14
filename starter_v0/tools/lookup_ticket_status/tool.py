from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


TICKET_FILE = ROOT / "helpdesk_data" / "tickets.json"


def lookup_ticket_status(ticket_id: str = "") -> dict[str, Any]:
    """Look up an existing IT ticket status by ticket ID."""
    try:
        wanted_id = (ticket_id or "").strip().upper()
        if not wanted_id:
            return {"tool": "lookup_ticket_status", "error": "missing_ticket_id"}

        if not TICKET_FILE.exists():
            return {"tool": "lookup_ticket_status", "ticket_id": wanted_id, "error": "ticket_not_found"}

        data = json.loads(TICKET_FILE.read_text(encoding="utf-8"))
        ticket = next((item for item in data.get("tickets", []) if item["ticket_id"] == wanted_id), None)
        if ticket is None:
            return {"tool": "lookup_ticket_status", "ticket_id": wanted_id, "error": "ticket_not_found"}

        return {"tool": "lookup_ticket_status", "ticket": ticket, "snapshot_at": data.get("snapshot_at")}
    except Exception as exc:
        return err("lookup_ticket_status", exc)
