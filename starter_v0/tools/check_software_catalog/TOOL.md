---
name: check_software_catalog
track: bonus
kind: local_knowledge
provider: mock_software_catalog
requires_env: []
inputs: [software, os, version]
outputs: [matches, snapshot_at, freshness, trust_boundary]
side_effect: false
---
# check_software_catalog

Team-built bonus tool. Looks up a software product or driver-update utility in
the fictional **approved software catalog** (`helpdesk_data/software_catalog.json`)
and returns its approval status (`approved`, `restricted`, `blocked`), approved
versions, install channel and notes. When a `version` is given it also returns a
`version_check` verdict (`approved`, `not_approved`, `review_required`).

## Why it exists

`KB-SW-009` says "chỉ cài phiên bản nằm trong approved software catalog", but no
starter tool could answer "is X approved / which version / where do I install it".
Without it the agent either guesses or sends the question to the wrong tool
(`search_kb`, `policy`, `search_device_info`).

## Contract

| Input | Type | Notes |
|---|---|---|
| `software` | string, required | Product name or alias, e.g. `Zoom`, `Dell Command Update` |
| `os` | enum `all\|windows\|macos\|ios\|android`, default `all` | Filters matches by platform |
| `version` | string, optional | If given, checked against approved versions / minimum version |

Output on success: `matches[]` (max 5, sorted by relevance) with
`software_id, name, vendor, category, status, os, approved_versions,
minimum_version, install_channel, requires_admin, notes[, version_check]`,
plus `snapshot_at`, `source`, `freshness`, `trust_boundary`.

Errors (never raise): `missing_software_name`, `software_name_too_long`,
`invalid_os`, `invalid_input_type`, `unexpected_internal_identifier`,
`software_not_found` (with `examples`).

## Guardrails

- Read-only: never installs, downloads or modifies anything (`side_effect: false`).
- Rejects asset/employee identifiers in the query — the catalog is about
  products, not people or devices.
- Unknown software is reported as **unapproved until reviewed**, never silently
  treated as allowed.
- Catalog text is reference data; no instruction-like content is executed.

## Smoke test

```bash
python -c "from tools import TOOL_FUNCTIONS as T; r=T['check_software_catalog']('zoom','macos','6.1.4'); print(r['matches'][0]['status'], r['matches'][0]['version_check'])"
python -c "from tools import TOOL_FUNCTIONS as T; print(T['check_software_catalog']('teamviewer')['matches'][0]['status'])"
python -c "from tools import TOOL_FUNCTIONS as T; print(T['check_software_catalog']('notepad++').get('error'))"
python -c "from tools import TOOL_FUNCTIONS as T; print(T['check_software_catalog']('zoom on LT-204').get('error'))"
```

PASS khi: dòng 1 in `approved {'requested': '6.1.4', 'verdict': 'approved', ...}`;
dòng 2 in `blocked`; dòng 3 in `software_not_found`; dòng 4 in
`unexpected_internal_identifier`. Script đầy đủ: `scripts/smoke_check_software_catalog.py`.
