# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team:
- Members:
- Provider/model:

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> Viết 1–2 câu mô tả capability và giới hạn của agent.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
|  |  |  |

## A3. Câu hỏi mẫu

1.
2.
3.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

### Baseline Summary
- 30 cases, 21 PASS, 9 FAIL, accuracy 0.70
- Failure split: wrong_tool 3 | missing_info 3 | wrong_boundary 3
- Mismatch split: missing_tool_call 5 | extra_tool_call 2 | wrong_arg_value 2
- Anomaly: tool_routing_accuracy 0.7667 vs wrong_tool=3 → flagged for review

### Per-Case Table

| Case | Failure Type | Expected Tool(s) | Actual Tool Call(s) | Expected Args | Actual Args | Root Cause | Category |
|---|---|---|---|---|---|---|---|
| H04_user_routing | wrong_tool | `lookup_user` | `inspect_device` | `{"employee_id":"EMP-1003"}` | N/A | `lookup_user` schema didn't differentiate clearly from `inspect_device`. | DESCRIPTION_OVERLAP |
| H10_missing_asset | missing_info | `clarify` | `inspect_device` | `{"response_type":"text"}` | `{"asset_id":"LT-204"}` (hallucinated) | `inspect_device` missed rules to block guessing and enforce `clarify`. | MISSING_WHEN_NOT_TO_USE |
| H11_missing_employee | missing_info | `clarify` | `lookup_user` | `{"response_type":"text"}` | N/A | `lookup_user` didn't explicitly forbid guessing missing IDs. | MISSING_WHEN_NOT_TO_USE |
| H12_confirm_before_ticket | wrong_boundary | `clarify` | `create_ticket` | `{"response_type":"yes_no"}` | `{"summary":...}` | `create_ticket` lacked explicit `confirm_required` boundary. | BOUNDARY_NOT_DECLARED |
| H13_parallel_status_and_device | wrong_tool | `check_service_status`, `inspect_device` | `inspect_device` | Multiple | N/A | Schema lacked instructions that tools can be called in parallel. | DESCRIPTION_OVERLAP |
| H17_triage_with_three_sources | wrong_tool | 3 tools | 1 tool | Multiple | N/A | Schema didn't support multi-source triage explicitly. | DESCRIPTION_OVERLAP |
| H19_ambiguous_environment | missing_info | `clarify` | `check_service_status` | `{"response_type":"choice"}` | `{"environment":"production"}` | `environment` lacked strict `required` flag, defaulting to prod. | SCHEMA_MISSING_PARAM |
| M05_ticket_confirmation | wrong_boundary | `clarify` | `create_ticket` | `{"response_type":"yes_no"}` | `{"priority":"high"}` | Agent didn't know it must stop at boundary after priority change. | BOUNDARY_NOT_DECLARED |
| M09_confirmation_invalidated | wrong_boundary | `clarify` | `create_ticket` | `{"response_type":"yes_no"}` | `{"confirmed":true}` | `create_ticket` lacked rule to invalidate old confirmation on arg change. | BOUNDARY_NOT_DECLARED |

### Cluster A — wrong_tool (H04, H13, H17)
- **Overlap Analysis:** `inspect_device` and `lookup_user` descriptions collided. H13 and H17 failed because the agent assumed one tool was enough.
- **Patches:** Added `when_NOT_to_use` to `inspect_device` banning employee queries. Added `when_to_use` rules stating tools can be called IN PARALLEL for triage.

### Cluster B — missing_info (H10, H11, H19)
- **Missing Requirements:** `check_service_status` relied on default `environment="production"` which failed on ambiguous inputs like "demo" (H19). `asset_id` and `employee_id` were loosely enforced.
- **Patches:** Made `environment`, `asset_id`, and `employee_id` strictly `required` with RegEx patterns. Added explicit `when_NOT_to_use` explicitly banning LLM hallucination and forcing `clarify`.

### Cluster C — wrong_boundary (H12, M05, M09)
- **Boundary Analysis:** `create_ticket` has write side-effects but lacked a `confirm_required` schema flag. This caused it to skip confirmation entirely or blindly reuse stale confirmations (M09).
- **Patches:** Added `boundaries.confirm_required: true` and failure modes explicitly instructing the agent to call `clarify` if `priority` or `summary` changes.

### Cross-Team Handoffs
- **TV1:** `system_prompt.md` needs an explicit "clarify before action" rule.
- **TV3:** `eval_group.json` cases H13/H17 expected output may be ambiguous; consider checking `tool_routing_accuracy` formula anomaly.
- **TV4:** Re-run `eval_adversarial.json` after these boundary patches.
- **TV5:** For any new tool, I will provide the schema.
## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Không làm phần này không ảnh hưởng việc hoàn thành core lab. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

Trong vai trò Tool Declaration & Schema Engineer, đợt baseline (30 cases, accuracy 0.70) đã cho tôi thấy rõ sự mong manh của việc phụ thuộc vào suy luận tự nhiên của LLM nếu không có schema chặt chẽ. Quyết định đầu tiên của tôi là loại bỏ sự lỏng lẻo của các kiểu `string` cơ bản. Ví dụ điển hình là H19: vì `environment` có default là `production`, LLM đã lười biếng bỏ qua việc hỏi lại người dùng khi gặp từ "demo". Tôi đã phải đánh đổi sự ngắn gọn của schema để thêm regex pattern `^(LT|DT)-[0-9]+$` và biến `environment` thành biến bắt buộc. Việc này ngay lập tức dập tắt các trường hợp missing_info (H10, H11) vì JSON Schema Validator sẽ chặn đứng LLM nếu nó cố bịa ID.

Thứ hai, boundary decisions đóng vai trò sống còn. Việc `create_ticket` gây ra hàng loạt lỗi wrong_boundary (H12, M05, M09) là minh chứng cho việc Agent không tự hiểu thế nào là "stale confirmation". Một khi user đổi priority (M05), payload đã thay đổi, nhưng Agent vẫn đâm đầu tạo ticket. Tôi đã bổ sung `confirm_required: true` vào khối `boundaries` và explicitly cảnh báo trong `when_NOT_to_use`.

Tuy nhiên, description overlap mới là rào cản đau đầu nhất. H04 fail vì `lookup_user` và `inspect_device` không có ranh giới rõ ràng. Bài học ở đây là `when_NOT_to_use` mang tính chất non-negotiable. Không chỉ bảo LLM *nên* làm gì, ta phải nói thẳng nó *tuyệt đối cấm* làm gì. Đối với v2 của tools.yaml, tôi dự định sẽ chuẩn hóa luôn khối `boundaries` thành một object độc lập để parser có thể mapping trực tiếp sang middleware bảo mật. 

Cuối cùng, sự phối hợp là chìa khóa. Tôi không thể nhét mọi quy tắc vào tools. Tôi đã chuyển giao cho TV1 việc cập nhật `system_prompt.md` để dặn dò "clarify before action", nhắc TV4 chạy lại luồng adversarial vì schema mới đã bọc lót kỹ hơn, và báo TV3 kiểm tra lại metric anomaly (0.7667 routing accuracy vs 3 wrong_tool). Sự phân định rõ ràng giữa Tool Schema (TV2) và System Prompt (TV1) giúp hệ thống dễ debug và vững chãi hơn rất nhiều.

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Reflection chung của nhóm

Các thành viên thảo luận và viết một reflection chung. Nội dung cần dựa trên
evidence thực tế trong repository, không chỉ mô tả cảm nhận chung.

- Mục tiêu nào của nhóm đã hoàn thành? Dẫn đến artifact hoặc run tương ứng.
- Hypothesis hoặc thay đổi nào tạo ra cải thiện rõ nhất?
- Failure quan trọng nào vẫn chưa xử lý được hoàn toàn?
- Nhóm đã phân chia, review và tích hợp công việc như thế nào?
- Nếu có thêm một vòng, nhóm sẽ ưu tiên thay đổi và kiểm chứng điều gì?

**Reflection chung của nhóm:**

> Viết reflection tại đây và dẫn link/path đến evidence liên quan.

## C2. Self-reflection của từng thành viên

Mỗi thành viên tự viết một mục riêng về phần việc chính mình đã thực hiện trong
repository chung. Không viết thay hoặc gộp nhiều thành viên vào một câu trả lời.
Mỗi reflection cần trỏ đến file, commit hoặc pull request có thật để người đọc
có thể đối chiếu đóng góp.

Sao chép mẫu dưới đây cho từng thành viên:

### Họ tên — MSSV

- **Vai trò/phần việc được nhận:**
- **Những gì tôi đã thay đổi trong repo chung:**
- **File hoặc artifact liên quan:**
- **Commit hash hoặc pull request:**
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
- **Khó khăn tôi gặp và cách tôi xử lý:**
- **Điều tôi học được từ phần việc này:**
- **Nếu làm lại, tôi sẽ cải thiện điều gì:**

Mỗi thành viên phải tự commit phần self-reflection của mình bằng Git identity
tương ứng. Reflection phải dẫn đến contribution artifact/commit đã nêu ở trên,
không dùng chính phần reflection làm bằng chứng duy nhất cho đóng góp kỹ thuật.

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAMMATES.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:
