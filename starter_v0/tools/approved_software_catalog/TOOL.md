---
name: approved_software_catalog
track: bonus
kind: local_knowledge
provider: mock_approved_software_catalog
requires_env: []
inputs: [query, category, operating_system, approval_status, top_k]
outputs: [results, snapshot_at, source, side_effect, trust_boundary]
side_effect: false
---
# approved_software_catalog

Searches the fictional Northstar Labs software approval catalog by product name,
capability, category, operating system, and approval state. It is a read-only
lookup: a result never installs software or authorizes a change.

The query must contain only software or capability terms. Asset IDs, employee
IDs, passwords, tokens, API keys, MFA/OTP values, and recovery codes are rejected
because they are unnecessary for a catalog lookup. An empty result means the
catalog has no matching record; it does not imply approval.
