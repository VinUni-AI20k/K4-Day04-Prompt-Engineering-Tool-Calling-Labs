# Role E — Security and bonus-tool evidence

`approved_software_catalog` is a team-built, deterministic local lookup over
`helpdesk_data/approved_software.json`. It fills the missing capability named in
the lab knowledge base: checking whether software is approved before suggesting
installation.

## Contract and integration

- Contract: `tools/approved_software_catalog/TOOL.md`
- Implementation: `tools/approved_software_catalog/tool.py`
- Registry: `tools/__init__.py`
- Model declaration: `artifacts/tools.yaml`
- Mock data: `helpdesk_data/approved_software.json`
- Team eval: `data/eval_group.json`, case `G10_approved_vpn_catalog`
- Deterministic evidence: `approved_software_catalog_smoke.json`
- Security evidence: `role_e_security_smoke.json`

The existing Streamlit UI discovers declarations from `tools.yaml` and renders
all tool events generically, so the bonus tool appears without a separate UI
loop or tool-specific UI code.

## Safety properties verified by the smoke test

- The tool is read-only and reports `side_effect: false`.
- It filters by operating system instead of presenting an incompatible package.
- It rejects asset and employee identifiers because they are unnecessary for a
  software-catalog lookup.
- It rejects credential-like values in the query.
- A catalog result is reference data; it cannot authorize installation or any
  other state change.

Run from `starter_v0/`:

```bash
python tools/approved_software_catalog/smoke_test.py
python scripts/role_e_security_smoke.py
```
