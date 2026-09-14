---
name: create_ticket
track: bonus
kind: action
provider: local_ticket_store
requires_env: []
inputs: [summary, priority, asset_id, confirmed]
outputs: [tool, status, ticket_id, path, error, message, max_length, priority]
side_effect: local_file_write
requires_confirmation: true
---
# create_ticket

Creates a local mock helpdesk ticket under `tickets/`. It returns
`needs_confirmation` and writes nothing unless `confirmed` is the literal
boolean `true`. It rejects missing or overlong summaries, invalid priorities or
asset IDs, and ticket summaries containing credentials, tokens, MFA values, or
recovery codes. This is the only declared state-changing tool.
