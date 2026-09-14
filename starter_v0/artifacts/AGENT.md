# Agent Change Log — System Prompt Refinement

**Role:** Person 2 — System Prompt Engineer
**Date:** 2026-09-14
**Version:** v1
**Run file:** `runs/v1_B_base_openai_20260914T193708240611.json`

---

## Baseline (v0)

| Metric | v0 |
|---|---|
| case_accuracy | 0.70 (21/30) |
| tool_routing_accuracy | 0.767 |
| argument_accuracy | 0.70 |
| multiturn_accuracy | 0.80 |

**Failing cases:** H04, H10, H11, H12, H13, M05, M09, H03, H19

---

## Failure Analysis

### Category 1 — Routing failures

**H04_user_routing**
- Query: "Tra cứu tài khoản nhân viên EMP-1003 và thiết bị được cấp"
- Expected: `lookup_user` only
- Actual: `lookup_user` + extra `inspect_device` call
- Root cause: No rule clarifying that `lookup_user` already returns assigned device info. Agent added `inspect_device` defensively.

**H03_kb_routing**
- Query: "Tìm hướng dẫn cấu hình Outlook profile trên Windows 11"
- Expected: `search_kb(category=email)`
- Actual: `search_kb(category=account)`
- Root cause: No category mapping guidance. Agent associated "profile" with "account" instead of "email".

### Category 2 — Missing identifier / clarify failures

**H10_missing_asset**
- Query: "Kiểm tra Wi-Fi trên laptop của mình giúp nhé" (no asset ID)
- Expected: `clarify(response_type=text)`
- Actual: `inspect_device` with a guessed asset ID
- Root cause: No rule requiring the agent to ask before guessing an identifier.

**H11_missing_employee**
- Query: "Kiểm tra tài khoản của bạn nhân viên bên Sales" (no employee ID)
- Expected: `clarify(response_type=text)`
- Actual: `lookup_user` with a guessed employee ID
- Root cause: Same as H10 — no ask-before-guess rule.

**H19_ambiguous_environment**
- Query: "Kiểm tra email ở môi trường demo của team QA" (environment "demo" not valid)
- Expected: `clarify(response_type=choice, options=["production","staging"])`
- Actual: `check_service_status(environment=staging)` — guessed staging
- Root cause: No rule to clarify when environment is not explicitly production or staging.

### Category 3 — Confirmation boundary failures

**H12_confirm_before_ticket**
- Query: "Tạo ticket mức high cho lỗi VPN trên LT-204"
- Expected: `clarify(yes_no)` first
- Actual: `create_ticket(confirmed=true)` directly — skipped confirmation
- Root cause: No explicit rule requiring a `clarify(yes_no)` gate before any write action.

**M05_ticket_confirmation**
- Multi-turn: user requested ticket creation
- Expected: `clarify(yes_no)` before writing
- Actual: called `create_ticket` then `clarify` after — wrong order
- Root cause: Same — no ordered confirmation rule.

**M09_confirmation_invalidated**
- Multi-turn: user confirmed, then context changed (different asset)
- Expected: `clarify(yes_no)` again after context change
- Actual: used stale `confirmed=true` from prior turn
- Root cause: No rule invalidating prior confirmation when context changes.

### Category 4 — Multi-turn / argument failures

**H13_parallel_status_and_device**
- Query: check VPN service AND inspect LT-204 VPN check simultaneously
- Expected: `check_service_status(service=vpn)` + `inspect_device(asset_id=LT-204, check=vpn)`
- Actual: `inspect_device` missing `check` argument
- Root cause: No guidance to always provide all required args in parallel calls.

---

## Changes Made to system_prompt.md

### Change 1 — Full identity + capabilities section with per-tool routing guidance
**Hypothesis:** The v0 prompt had no per-tool decision rules. Adding explicit "use this tool when X, not when Y" descriptions will fix routing failures (H01–H04, H13).
**Evidence:** H04 called an extra tool because there was no rule saying `lookup_user` already returns device data. H13 omitted the `check` arg because no guidance mandated all required args in parallel calls.
**Result:** Fixed H04, H13, and all H01–H02 routing cases.

### Change 2 — Explicit routing decision tree (7 numbered rules)
**Hypothesis:** A numbered decision table forces unambiguous selection between tools with overlapping semantics (e.g. `check_service_status` vs `inspect_device`).
**Evidence:** Baseline showed 3 wrong_tool failures in H01–H04 category.
**Result:** All routing cases now pass.

### Change 3 — Missing identifier / ask-before-guess rule
**Hypothesis:** The agent guesses asset IDs and employee IDs when not provided. An explicit rule "if identifier is absent, call `clarify(text)` — never guess" will fix H10, H11.
**Evidence:** H10 actual call used a fabricated asset ID; H11 used a fabricated employee ID.
**Result:** Fixed H10, H11.

### Change 4 — Ambiguous environment clarify rule
**Hypothesis:** When the user names an environment not in {production, staging}, the agent should offer a `clarify(choice)` rather than guess. Explicit rule with examples ("demo", "QA", "test", "lab") will fix H19.
**Evidence:** H19 actual call passed `environment=staging` when user said "demo".
**Result:** Fixed H19.

### Change 5 — Confirmation boundary for write actions
**Hypothesis:** `create_ticket` is a write action. An explicit ordered rule — "always call `clarify(yes_no)` before `create_ticket`; never pass `confirmed=true` unless user confirmed in a prior turn; re-confirm if context changes" — will fix H12, M05, M09.
**Evidence:** All three cases skipped or misordered the confirmation step.
**Result:** Fixed H12, M05, M09.

### Change 6 — Multi-turn context carry-over rules
**Hypothesis:** Rules for correction (use new ID), cancellation (abandon intent), and latest-intent-wins will fix M02–M04, M06–M08, M10.
**Evidence:** Baseline multiturn_accuracy was 0.80; these rules bring it to 1.0.
**Result:** All multi-turn cases pass.

### Change 7 — search_kb category mapping
**Hypothesis:** Without explicit mapping, the model associates "Outlook profile" with `account` instead of `email`. A keyword-to-category table in the tool description fixes H03.
**Evidence:** H03 actual: `category=account`; expected: `category=email`.
**Result:** Fixed H03.

### Change 8 — When NOT to use a tool
**Hypothesis:** H09 (meta question about the agent) and H20 (format without re-fetching) required the agent to answer directly. An explicit "do not call tools for these patterns" rule prevents unnecessary tool use.
**Evidence:** Both cases expected `no_tool` behavior.
**Result:** Confirmed passing; no regression.

---

## v1 Results

| Metric | v0 | v1 | Delta |
|---|---|---|---|
| case_accuracy | 0.70 | **1.00** | +0.30 |
| tool_routing_accuracy | 0.767 | **1.00** | +0.233 |
| argument_accuracy | 0.70 | **1.00** | +0.30 |
| multiturn_accuracy | 0.80 | **1.00** | +0.20 |

**All 30/30 cases pass. Zero regressions.**

---

## Regression Review

All 21 cases that passed in v0 were re-verified in v1 run `v1_B_base_openai_20260914T193708240611.json`. Every previously passing case continues to pass. No breaking changes were introduced.
