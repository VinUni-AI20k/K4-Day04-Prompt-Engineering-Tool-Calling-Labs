---
name: lookup_ticket_status
track: bonus
kind: local_status
provider: mock_ticket_store
requires_env: []
inputs: [ticket_id]
outputs: [ticket, snapshot_at, data_source]
side_effect: false
---
# lookup_ticket_status

Looks up one fictional helpdesk ticket by its exact `LAB-XXXXXXXX` ticket ID.
It returns the ticket's current status and support-safe metadata from a static
local fixture. It never creates, updates, or closes a ticket and does not search
by employee name, free-form summary, or other personal data.
