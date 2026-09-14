---
name: lookup_user
track: core
kind: local_directory
provider: mock_employee_directory
requires_env: []
inputs: [employee_id]
outputs: [tool, employee, snapshot_at]
side_effect: false
---
# lookup_user

Looks up one fictional employee by employee ID. The support-safe metadata and
`assigned_assets` are nested inside the returned `employee` object; the other
top-level field is `snapshot_at`. It never returns credentials or secrets.
An unknown ID returns `error: employee_not_found`.
