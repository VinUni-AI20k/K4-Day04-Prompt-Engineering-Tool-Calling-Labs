---
name: lookup_ticket_status
track: bonus
kind: local_status
provider: mock_ticket_status_catalog
requires_env: []
inputs: [ticket_id]
outputs: [ticket_id, status, priority, asset_id, updated_at]
side_effect: false
---
# lookup_ticket_status

Reads a deterministic, anonymized ticket-status catalog. It accepts only a
ticket ID in the `LAB-XXXXXXXX` format and never accepts a file path or reads
the generated `tickets/` directory. It returns `invalid_ticket_id` for invalid
input and `ticket_not_found` for an unknown valid ID.

The tool is read-only and returns no credentials, user records, or diagnostic
logs.
