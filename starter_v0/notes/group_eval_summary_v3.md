# Group eval summary - v3

Run file:

```text
starter_v0/runs/v3_B_group_openai_20260914T200739218485.json
```

Provider/model:

```text
openai / gpt-4o-mini
```

Summary:

| Metric | Value |
|---|---:|
| total_cases | 10 |
| measured_cases | 10 |
| provider_error_cases | 0 |
| passed_cases | 5 |
| case_accuracy | 0.50 |
| tool_routing_accuracy | 0.80 |
| argument_accuracy | 0.50 |
| multiturn_accuracy | 0.60 |

## Passed cases

| Case | What passed |
|---|---|
| G02_linux_laptop_security | Correctly inspected `LT-411` with `check=security` |
| G05_public_driver_search | Correctly used external public device search |
| G06_multiturn_asset_correction | Correctly used latest corrected asset `DT-087` |
| G07_multiturn_cancel_ticket | Correctly respected cancellation with no tool |
| G08_multiturn_confirm_revised_ticket | Correctly created confirmed revised ticket payload |

## Failed cases

| Case | Failure | Suggested owner |
|---|---|---|
| G01_wifi_floor4_status | Expected `environment=production`, actual omitted environment | Nguoi 3: clarify `check_service_status.environment` defaults/required behavior |
| G03_disabled_user_lookup | Extra `inspect_device` after `lookup_user` | Nguoi 2: remind that assigned assets in user lookup are enough unless user asks to inspect |
| G04_policy_external_tools | Expected `policy_area=external_tools`, actual `data_privacy` | Nguoi 3: sharpen policy area routing examples |
| G09_multiturn_environment_choice | Expected `clarify(choice)`, actual `check_service_status` | Nguoi 2+3: unsupported env labels must not be guessed |
| G10_multiturn_internal_external_boundary | Expected Apple/MacBook from inspected asset, actual Lenovo/ThinkPad | Nguoi 2: after internal lookup, use returned public manufacturer/model for external search |

## Next fix hypothesis

If the prompt explicitly says "do not infer missing enum arguments from defaults in eval/tool calls" and `tools.yaml` gives stronger examples for policy areas and internal-to-external product identity, group eval accuracy should improve without changing tool implementation.

