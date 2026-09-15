---
name: ticket_status_lookup
track: bonus
kind: local_read_only
provider: local_ticket_store
requires_env: []
inputs: [ticket_id]
outputs: [status, ticket_id, summary, priority, asset_id, created_at]
side_effect: false
---
# ticket_status_lookup

Looks up one existing local helpdesk ticket by its exact ticket ID. It is
read-only and never creates, updates, or deletes tickets. Unknown or malformed
IDs return a clear error without guessing.
