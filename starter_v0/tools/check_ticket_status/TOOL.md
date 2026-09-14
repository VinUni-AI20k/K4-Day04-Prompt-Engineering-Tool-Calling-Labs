---
name: check_ticket_status
track: bonus
kind: local_ticket_lookup
provider: mock_ticket_store
requires_env: []
inputs: [ticket_id]
outputs: [ticket]
side_effect: false
---
# check_ticket_status

Looks up an existing IT helpdesk ticket or incident by its ID (such as INC-1042, TCK-2026-001, or local LAB-* tickets).
Returns the ticket's current resolution status, priority, assigned team, category, and recent resolution notes.
This tool is read-only and does not create, update, or close tickets.
