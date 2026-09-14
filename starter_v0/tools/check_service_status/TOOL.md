---
name: check_service_status
track: core
kind: local_status
provider: mock_status_page
requires_env: []
inputs: [service, environment]
outputs: [tool, service, environment, status, incident, incident_id, affected_locations, started_at, last_updated, workaround, checked_at]
side_effect: false
---
# check_service_status

Reads the deterministic mock status page for a named shared service and
environment. It does not diagnose a single employee device. A missing service
and environment pair returns `error: not_found` plus `available_services`.
