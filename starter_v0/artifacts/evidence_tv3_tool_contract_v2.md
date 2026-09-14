# TV3 Evidence: Tool Contract v2

Date: 2026-09-14
Owner: TV3
Scope: declarations, tool contracts, registry synchronization, and smoke tests.

## Audit Basis

- Registry: `tools/__init__.py`
- Implementations: `tools/*/tool.py`
- Declarations: `artifacts/tools.yaml`
- Documentation: `tools/*/TOOL.md`
- Invocation paths: `agent.py`, `chat.py`, and `run_eval.py`

The registry contains these nine names and the v2 declaration contains the same
nine names: `clarify`, `search_kb`, `check_service_status`, `inspect_device`,
`lookup_user`, `format_incident_report`, `policy`, `create_ticket`, and
`search_device_info`.

## Declaration Changes

Before: starter declarations had short descriptions and limited input schemas.
After: `tools.yaml` is marked `contract_version: v2` and documents:

- Required inputs, defaults, enums, formats, lengths, and result limits.
- Internal read-only, external read-only, control, and state-changing boundaries.
- Knowledge-base, policy, and web-result trust boundaries.
- `create_ticket` confirmation as literal boolean `true`, with sensitive-data,
  asset, summary length, and local-write behavior.
- Clear distinction between shared service status and one-device inspection.
- Clear distinction between local policy/KB search and external public-product
  search.

The nine `TOOL.md` files were synchronized with actual output fields and error
behavior. No implementation, system prompt, dataset, UI, or business logic was
changed.

## Smoke Test Command

Executed from `starter_v0`:

```powershell
python -m compileall -q .
python -c "... registry, valid, error, boundary, confirmation, and external checks ..."
```

The executed checks were:

- YAML load, provider conversion, and declaration-to-registry set equality.
- Valid calls for `clarify`, `search_kb`, `check_service_status`,
  `inspect_device`, `lookup_user`, `format_incident_report`, and `policy`.
- Missing asset handling and restricted internal identifier handling.
- Sensitive-data rejection in ticket summaries.
- String confirmation rejection, invalid priority, and invalid asset rejection.
- Confirmed ticket creation followed by existence verification and cleanup.
- External search without `TAVILY_API_KEY`.

## Results

```text
contract_registry_sync: PASS
valid_calls: PASS
missing_and_boundary_errors: PASS
action_boundary: PASS
confirmed_write_and_cleanup: PASS
runtime_invalid_enum_status= not_found
runtime_wrong_type_confirmed= needs_confirmation
external_missing_key= missing_api_key
```

The initial baseline command from the repository root failed with
`ModuleNotFoundError: No module named 'tools'`; rerunning from `starter_v0`,
the documented runtime directory, passed. This was an invocation-directory
issue, not a declaration issue.

## Findings

1. Tool: `policy`
   Problem: registry/declaration name is `policy`, but the implementation
   response currently returns `tool: search_company_policy`.
   Expected: response identity should use the exposed registry name `policy`.
   Actual: `tool: search_company_policy`.
   Root cause: implementation function/response naming differs from the public
   registry name.
   Severity: Medium.
   Ownership: implementation owner, not TV3. No implementation change made.

2. Tools: `clarify`, `search_kb`, `check_service_status`, `inspect_device`,
   `format_incident_report`, and `policy`
   Problem: direct runtime calls do not independently reject every invalid enum;
   they normalize or return an empty/not-found result.
   Expected: implementation-level validation should match the schema boundary.
   Actual: for example, `check_service_status('vpn', 'invalid')` returns
   `error: not_found` rather than `invalid_environment`.
   Root cause: validation is primarily expressed in the declaration, not in the
   implementation.
   Severity: Low for model calls, Medium for direct callers.
   Ownership: implementation owner if strict runtime rejection is required.

3. Tool: `create_ticket`
   Problem: a wrong-type confirmation value is accepted by the Python function
   but treated as not confirmed.
   Expected: invalid confirmation type should return a distinct type error.
   Actual: `confirmed='true'` returns `status: needs_confirmation` and does not
   write a file.
   Root cause: implementation checks `confirmed is not True` as a safety gate,
   but does not report a type-specific error.
   Severity: Low; the write boundary remains safe.
   Ownership: implementation owner if type-specific errors are required.

4. Tools: all declarations
   Problem: there is no independent JSON Schema validator in the repository.
   Expected: provider-facing schema conversion plus optional validation test.
   Actual: YAML loading and provider conversion are tested; provider/API
   enforcement is delegated to the provider.
   Root cause: no schema-validation dependency or validation layer is present.
   Severity: Low.
   Ownership: shared infrastructure owner if formal schema validation is needed.

## Cross-Owner Issues

- `policy` response identity should be aligned in `tools/policy/tool.py`.
- Runtime enum/type rejection could be strengthened in implementations.
- A formal schema validator could be added outside TV3 scope.
- `artifacts/system_prompt.md`, evaluation datasets, UI/application code, and
  business logic were intentionally not modified.
