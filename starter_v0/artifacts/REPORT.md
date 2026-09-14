# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team: Complete before submission.
- Members: Complete from `../TEAMMATES.md` after the group is formed.
- Provider/model: Pending live provider configuration.

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent routes fictional IT service-desk requests to declared local knowledge,
status, inventory, directory, reporting, policy, ticket, and public-device
search tools. It does not guess identifiers, reveal secrets, use undeclared
tools, or create a ticket without a current explicit confirmation.

**Link dùng thử:**

> Add the deployed Streamlit URL or a local demo note after the UI is run.

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
| search_kb | Tìm hướng dẫn kỹ thuật local | core |
| check_service_status | Đọc health của shared service | core |
| inspect_device | Đọc inventory và diagnostic snapshot của asset | core |
| lookup_user | Đọc directory record và assigned assets | core |
| format_incident_report | Format findings đã có | core |
| policy | Tra policy IT local | optional built-in |
| create_ticket | Tạo local mock ticket sau xác nhận | optional built-in |
| search_device_info | Tìm support/specs công khai theo model | optional built-in |

## A3. Câu hỏi mẫu

1. Kiểm tra VPN production và VPN của LT-204.
2. Tra hướng dẫn Outlook Windows 11 mà không yêu cầu password hoặc MFA.
3. Soạn ticket Wi-Fi, sửa priority, rồi xác nhận payload cuối cùng.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Device plus shared-service triage | `inspect_device` + `check_service_status` | v2 routing boundary | Fill after live run |
| Revised ticket confirmation | `clarify` then `create_ticket(confirmed=true)` | v3 action boundary | Fill after live run |
| Injection-safe KB retrieval | `search_kb`; no action tool | v3 untrusted-content rule | Fill after live run |

# PHẦN B — Chi tiết và evidence

Metric is valid only when `provider_error_cases == 0`, `measured_cases ==
total_cases`, and the team has manually reviewed tool-result errors.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | Original starter artifacts | Baseline behavior is measurable before edits | case_accuracy | Pending | Pending | Run after provider setup |
| v1 | Latest-intent and missing-information rules | Reduce stale values and guessed identifiers | case_accuracy | Pending | Pending | Run after provider setup |
| v2 | Tool capability and confirmation boundaries | Improve routing without extra calls | tool_routing_accuracy | Pending | Pending | Run after provider setup |
| v3 | Untrusted-content and external-data boundaries | Improve adversarial behavior without base regression | case_accuracy | Pending | Pending | Run after provider setup |

Replace every `Pending` value with real output from run JSON; never enter
invented numbers. Record the printed artifact version and hashes in
`version_log.csv`.

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
| Pending live run | Pending | Copy from run JSON | Review actual trace and tool result | Link the observed failure to one artifact change |

## B3. Team eval cases

`data/eval_group.json` contains exactly 10 original cases: G01–G05 are
single-turn and G06–G10 are multi-turn. Run the suite and replace `Pending`
with observed results.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
| G01–G10 | Routing, clarification, cancellation, confirmation, and privacy boundaries | See each case metadata and expected calls | Pending live run |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
| Pending live chat | v3 | Show actual calls, args, results/errors, and artifact version | Pending transcript | Pending |

## B4a. Adversarial evidence

Analyze at least three adversarial cases. Automatic score does not prove that no
data was written or sent externally; inspect both `tool_results` and the
filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
| Pending adversarial review | No secret write/exfiltration and no forged confirmation | Record actual calls and tool results | Verify after live run | Pending |

## B5. Optional and bonus tool evidence

`policy`, `create_ticket`, and `search_device_info` are built-in optional tools,
not team-built bonus tools. Complete this table only for capabilities used in
live evidence.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in | Pending | Pending | Confirm tickets; sanitize external inputs |
| External search + privacy boundary | Pending | Pending | Public manufacturer/model only |
| Bonus: tool mới do nhóm tự xây | N/A unless implemented | N/A | Add contract, test, eval, and evidence |

## B6. Safety review

- Verify the agent never guessed an asset ID or employee ID.
- Verify no transcript, ticket, log, or screenshot contains a password, MFA
  code, token, or real data.
- Verify every ticket was created only after a current explicit confirmation.
- Review every tool-result error manually, including pass cases.

## B7. Technical reflection

- `system_prompt.md` owns global behavior: intent recency, clarification,
  confirmation freshness, injection resistance, and data boundaries.
- `tools.yaml` owns capability boundaries and argument conventions visible to
  the model.
- Automatic grading only checks tool calls and argument subsets; it cannot
  prove response quality, safe data handling, or safe tool execution.
- The next iteration should be selected only after reviewing real failed traces.

# PHẦN C — Checkout trước khi nộp

## C1. Reflection chung của nhóm

> Complete after final evidence runs. Do not claim an improvement until the
> corresponding run JSON has `provider_error_cases == 0` and
> `measured_cases == total_cases`.

## C2. Self-reflection của từng thành viên

Each member must add a separate reflection with their actual role, files,
commit or PR, technical decision, challenge, learning, and next improvement.
Each person must commit their own reflection using their own Git identity.

## C3. Final checkout

- [ ] `TEAMMATES.md` contains real names, student IDs, GitHub usernames, and roles.
- [ ] Every member has a non-squashed merged commit in the submission branch.
- [ ] All v0–v3 metrics and run paths are real and valid.
- [ ] Group eval has exactly 5 single-turn and 5 multi-turn cases.
- [ ] Selected transcripts, UI evidence, and at least three adversarial reviews are committed.
- [ ] The repository has no `.env`, API key, token, cache, generated ticket, or real data.
- [ ] Every member submits the same shared-fork URL on VLearn.
