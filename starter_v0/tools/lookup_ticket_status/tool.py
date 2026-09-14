from __future__ import annotations

import json
import re
from json import JSONDecodeError
from typing import Any

from tools._shared import ROOT, err


TICKET_STATUS_FILE = ROOT / "helpdesk_data" / "ticket_status.json"
TICKET_ID_PATTERN = re.compile(r"^LAB-[A-F0-9]{8}$", re.IGNORECASE)


def lookup_ticket_status(ticket_id: str = "") -> dict[str, Any]:
    if not isinstance(ticket_id, str):
        return {"tool": "lookup_ticket_status", "error": "invalid_ticket_id_type"}

    normalized_id = ticket_id.strip().upper()
    if not normalized_id:
        return {"tool": "lookup_ticket_status", "error": "missing_ticket_id"}
    if not TICKET_ID_PATTERN.fullmatch(normalized_id):
        return {
            "tool": "lookup_ticket_status",
            "ticket_id": normalized_id,
            "error": "invalid_ticket_id",
        }

    try:
        data = json.loads(TICKET_STATUS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"tool": "lookup_ticket_status", "error": "ticket_data_unavailable"}
    except JSONDecodeError:
        return {"tool": "lookup_ticket_status", "error": "invalid_ticket_data"}
    except Exception as exc:
        return err("lookup_ticket_status", exc)

    tickets = data.get("tickets")
    if not isinstance(tickets, list):
        return {"tool": "lookup_ticket_status", "error": "invalid_ticket_data"}

    ticket = next(
        (
            item
            for item in tickets
            if isinstance(item, dict) and str(item.get("ticket_id", "")).upper() == normalized_id
        ),
        None,
    )
    if ticket is None:
        return {
            "tool": "lookup_ticket_status",
            "ticket_id": normalized_id,
            "error": "ticket_not_found",
        }

    return {
        "tool": "lookup_ticket_status",
        "ticket": ticket,
        "snapshot_at": data.get("snapshot_at"),
        "data_source": "fictional_local_ticket_status",
    }
