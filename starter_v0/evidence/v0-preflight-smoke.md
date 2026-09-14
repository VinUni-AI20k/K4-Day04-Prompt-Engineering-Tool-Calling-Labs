# v0 Provider Preflight and Local Tool Smoke Evidence

## Environment

- Date: 2026-09-14
- Provider: `openai`
- Model: `gpt-4o-mini` (provider default)
- Python compile: PASS

## Provider preflight

Command:

```bash
python scripts/preflight_provider.py --provider openai
```

Observed result:

```text
OK provider=openai model=gpt-4o-mini
tool=check_service_status
args={'service': 'vpn', 'environment': 'production'}
```

The provider returned a structured tool call with the expected tool and arguments.

## Local tool smoke checks

| Check | Result |
|---|---|
| `clarify` | PASS, returned `awaiting_user=true` |
| `search_kb` | PASS, returned results and a trust boundary |
| `check_service_status` | PASS, returned VPN production status |
| `inspect_device` | PASS, returned LT-318 VPN diagnostics |
| `lookup_user` | PASS, returned EMP-1007 |
| `format_incident_report` | PASS, returned one formatted finding |
| `policy` | PASS, returned policy results and a trust boundary |
| `create_ticket` dry run | PASS, returned `needs_confirmation` |
| `create_ticket` with string confirmation | PASS, did not create a ticket |
| `create_ticket` with numeric confirmation | PASS, did not create a ticket |

The ticket directory contained zero JSON files before and after the smoke checks.
The external `search_device_info` smoke check was skipped because `TAVILY_API_KEY` was not configured and it is not a local-tool requirement.
