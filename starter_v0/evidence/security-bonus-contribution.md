# Security and Bonus Tool Evidence

Contributor: Nguyen Tuan Thanh (`Chika1357`)
Role: E - Security and Bonus Tool

## Tavily privacy boundary

`search_device_info` sends only public manufacturer, model, query type, and a
bounded result limit. It rejects asset/employee identifiers plus serial,
hostname, IP, location, diagnostics, and ticket-related labels before any HTTP
request. Official domains are preferred for known vendors, and instruction-like
web lines are separated into `untrusted_text`.

Deterministic evidence:

```powershell
python scripts/security_smoke.py
```

Observed result on 2026-09-14: 6/6 checks passed. The mocked HTTP client also
proved that blocked payloads caused zero network calls.

## Generated-ticket hygiene

The ticket writer accepts only literal Boolean `confirmed=True` and rejects
common credential fields before writing. `scripts/audit_tickets.py` performs a
read-only checkout for malformed, placeholder, sensitive, mismatched, or
duplicate generated tickets.

```powershell
python scripts/audit_tickets.py
```

Observed result on 2026-09-14: clean, 0 generated ticket files present.
Generated tickets remain ignored and must not be committed as evidence.

## Bonus tool: approved software catalog

`approved_software_catalog` is a new read-only capability backed by synthetic
JSON. It supports name/alias search and platform filtering, and preserves the
distinction among `approved`, `restricted`, and `prohibited`. A catalog result
does not install software or approve an exception.

Included artifacts:

- `tools/approved_software_catalog/TOOL.md`
- `tools/approved_software_catalog/tool.py`
- `helpdesk_data/approved_software.json`
- registry entry in `tools/__init__.py`
- model-facing schema in `artifacts/tools.yaml`
- `scripts/bonus_tool_smoke.py`

```powershell
python scripts/bonus_tool_smoke.py
```

Observed result on 2026-09-14: 6/6 checks passed; declaration/registry parity
also passed with 10 tools.

## Evidence still requiring the final team branch

- Keep `G-SW01_approved_software_lookup` in the final set of exactly 10 original
  cases, then run it with the selected provider and final artifact version.
- Capture a UI/transcript trace and copy the measured result into REPORT B5.
- Run the fixed adversarial suite with no provider errors, then fill REPORT B4a
  from actual calls, tool results, and filesystem inspection.
