from __future__ import annotations

import tempfile
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.lookup_ticket_status import tool as ticket_status_module


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"PASS {label}")


def main() -> None:
    fixture_before = ticket_status_module.TICKET_STATUS_FILE.read_bytes()

    existing = ticket_status_module.lookup_ticket_status("LAB-A1B2C3D4")
    check(existing.get("ticket", {}).get("status") == "open", "existing ticket status lookup")

    normalized = ticket_status_module.lookup_ticket_status("  lab-b2c3d4e5  ")
    check(normalized.get("ticket", {}).get("ticket_id") == "LAB-B2C3D4E5", "ticket ID normalization")

    check(ticket_status_module.lookup_ticket_status(123).get("error") == "invalid_ticket_id_type", "invalid ticket ID type")  # type: ignore[arg-type]
    check(ticket_status_module.lookup_ticket_status(" ").get("error") == "missing_ticket_id", "missing ticket ID")
    check(ticket_status_module.lookup_ticket_status("INC-123").get("error") == "invalid_ticket_id", "invalid ticket ID format")
    check(ticket_status_module.lookup_ticket_status("LAB-FFFFFFFF").get("error") == "ticket_not_found", "unknown ticket ID")

    with tempfile.TemporaryDirectory(prefix="ticket-status-smoke-") as temp_dir:
        invalid_file = Path(temp_dir) / "invalid.json"
        invalid_file.write_text("not-json", encoding="utf-8")
        with patch.object(ticket_status_module, "TICKET_STATUS_FILE", invalid_file):
            check(ticket_status_module.lookup_ticket_status("LAB-A1B2C3D4").get("error") == "invalid_ticket_data", "invalid fixture data")

        missing_file = Path(temp_dir) / "missing.json"
        with patch.object(ticket_status_module, "TICKET_STATUS_FILE", missing_file):
            check(ticket_status_module.lookup_ticket_status("LAB-A1B2C3D4").get("error") == "ticket_data_unavailable", "missing fixture data")

    check(ticket_status_module.TICKET_STATUS_FILE.read_bytes() == fixture_before, "lookup leaves fixture unchanged")
    print("PASS all lookup_ticket_status smoke checks")


if __name__ == "__main__":
    main()
