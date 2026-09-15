from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.ticket_status_lookup.tool import ticket_status_lookup


TICKET_DIR = ROOT / "tickets"


def main() -> None:
    ticket_path = next(TICKET_DIR.glob("LAB-*.json"), None)
    if ticket_path is None:
        raise SystemExit("No local ticket fixture found.")

    ticket_id = json.loads(ticket_path.read_text(encoding="utf-8"))["ticket_id"]
    found = ticket_status_lookup(ticket_id)
    missing = ticket_status_lookup("LAB-00000000")

    assert found["status"] == "open"
    assert found["ticket_id"] == ticket_id
    assert missing["error"] == "ticket_not_found"
    print(f"found={found['ticket_id']} status={found['status']}")
    print(f"missing={missing['ticket_id']} error={missing['error']}")


if __name__ == "__main__":
    main()
