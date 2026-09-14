from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err


TICKET_DIR = ROOT / "tickets"
STATIC_TICKETS_FILE = ROOT / "helpdesk_data" / "tickets.json"
TICKET_ID_PATTERN = re.compile(r"^(?:LAB-[A-F0-9]{8}|INC-\d{4})$", re.IGNORECASE)


def lookup_ticket(ticket_id: str = "") -> dict[str, Any]:
    if not isinstance(ticket_id, str):
        return {"tool": "lookup_ticket", "error": "invalid_ticket_id_type"}
    wanted_id = (ticket_id or "").strip().upper()
    if not wanted_id:
        return {"tool": "lookup_ticket", "error": "missing_ticket_id"}
    if not TICKET_ID_PATTERN.fullmatch(wanted_id):
        return {
            "tool": "lookup_ticket",
            "ticket_id": wanted_id,
            "error": "invalid_ticket_id_format",
            "expected_format": "LAB-XXXXXXXX or INC-XXXX",
        }

    try:
        # 1. Check dynamic local tickets created by create_ticket
        local_file = TICKET_DIR / f"{wanted_id}.json"
        if local_file.is_file():
            data = json.loads(local_file.read_text(encoding="utf-8"))
            return {
                "tool": "lookup_ticket",
                "ticket_id": data.get("ticket_id", wanted_id),
                "status": data.get("status", "open"),
                "summary": data.get("summary", ""),
                "priority": data.get("priority", "medium"),
                "asset_id": data.get("asset_id"),
                "requester_id": data.get("requester_id", "current_user"),
                "assignee_id": data.get("assignee_id", "unassigned"),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("created_at", ""),
                "notes": data.get("notes", "Ticket logged locally; waiting for triage."),
                "source": "local_ticket_store",
            }

        # 2. Check static mock tickets database
        if STATIC_TICKETS_FILE.is_file():
            data = json.loads(STATIC_TICKETS_FILE.read_text(encoding="utf-8"))
            for item in data.get("tickets", []):
                if item.get("ticket_id", "").upper() == wanted_id:
                    return {
                        "tool": "lookup_ticket",
                        **item,
                        "source": "helpdesk_system_records",
                        "snapshot_at": data.get("snapshot_at"),
                    }

        return {
            "tool": "lookup_ticket",
            "ticket_id": wanted_id,
            "error": "not_found",
            "message": f"Ticket {wanted_id} was not found in the helpdesk system.",
        }
    except Exception as exc:
        return err("lookup_ticket", exc)
