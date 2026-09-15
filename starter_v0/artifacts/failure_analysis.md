# Failure analysis log

Provider/model: `gemini` / `gemini-3.5-flash-lite` (free tier; `*-flash` models chỉ có 20 req/ngày nên không dùng được).
Run được dùng làm evidence chỉ khi `provider_error_cases == 0` và `measured_cases == total_cases`.

## v0 — `runs/v0_B_base_gemini_20260914T191518939050.json`

case_accuracy 0.70 · routing 0.767 · args 0.70 · multiturn 0.60 · 9/30 FAIL.

### Nhóm A — Trả JSON text thay vì gọi tool (H07, H12, M01, M03, M05)

```text
Case: H12_confirm_before_ticket
Expected calls: clarify(response_type=yes_no)
Actual calls: [] — text = {"action":"create_ticket","reply":"Đã tạo ticket ưu tiên high cho lỗi VPN trên thiết bị LT-204."}
Observed mismatch: missing_tool_call
Tool execution result: không có (không tool nào chạy) — nhưng reply tuyên bố ĐÃ tạo ticket → hallucinated action
Giả thuyết nguyên nhân: prompt starter yêu cầu "Return valid JSON with intent/action/reply"; model coi JSON là hành động thay cho tool call
Artifact dự định sửa: system_prompt.md — tool call là cách duy nhất để hành động; JSON reply chỉ dùng cho câu trả lời cuối; không được nói "đã làm" khi chưa có tool result
Metric dự kiến thay đổi: case_accuracy 0.70 → ≥0.85 (5 case nhóm A)
Rủi ro regression: no_tool cases (H08, H09, H14, M07) có thể bắt đầu gọi tool thừa nếu rule "luôn gọi tool" viết quá mạnh
```

Cùng pattern: H07 (format), M01/M03 (inspect_device sau khi có đủ asset ID), M05 (review rồi hỏi xác nhận nhưng không gọi `clarify`).

### Nhóm B — `clarify` sai `response_type` (H10, H11)

```text
Case: H10_missing_asset
Expected calls: clarify(response_type=text)
Actual calls: clarify(response_type=choice, options=["Nhập mã tài sản...", "Kiểm tra chung trạng thái Wi-Fi..."])
Observed mismatch: wrong_arg_value
Giả thuyết nguyên nhân: declaration clarify không nói khi nào dùng text/yes_no/choice; model tự bịa options
Artifact dự định sửa: tools.yaml — convention: text = hỏi identifier/giá trị tự do; yes_no = xin xác nhận action; choice = chỉ khi đáp án thuộc enum cố định của tool
Metric dự kiến: argument_accuracy tăng 2 case
Rủi ro regression: H19 cần choice [production, staging] — rule phải giữ được trường hợp này
```

### Nhóm C — Đoán environment (H19)

```text
Case: H19_ambiguous_environment
Expected calls: clarify(response_type=choice, options=[production, staging])
Actual calls: check_service_status(service=email, environment=staging)
Giả thuyết nguyên nhân: "môi trường demo của team QA" không thuộc enum; model tự map demo→staging
Artifact dự định sửa: tools.yaml (environment: chỉ điền khi user nói rõ production/staging; từ khác → hỏi) + prompt rule "không đoán giá trị enum"
```

### Nhóm D — Stale confirmation (M09)

```text
Case: M09_confirmation_invalidated
Expected calls: clarify(response_type=yes_no)
Actual calls: policy(query="incident priority critical data loss")
Giả thuyết nguyên nhân: không có rule "confirmation gắn với payload; payload đổi thì hỏi lại"
Artifact dự định sửa: system_prompt.md
```

### Ghi chú kỹ thuật

- `providers/gemini_provider.py` không truyền `tool_choice` sang Gemini, nên `tool_choice="required"` của evaluator không có hiệu lực với provider này → model được tự do trả text. Điều này làm nhóm A lộ ra rõ hơn so với OpenAI provider; đây là hành vi thật của agent trong chat (chat không dùng tool_choice) nên sửa bằng prompt là đúng chỗ.
- Đã thêm retry/backoff (429, 5xx, lỗi mạng) vào `gemini_provider.py` để run không bị `provider_error` do rate limit free tier. Không đổi logic model.

## v1 — `runs/v1_B_base_gemini_20260914T191918423640.json` (chỉ sửa `system_prompt.md`)

case_accuracy 0.70 → **0.867** · routing 0.90 · multiturn 0.60 → 0.90 · 4/30 FAIL · không regression.
Nhóm A (5 case) và nhóm D (M09) đã pass. no_tool cases (H08, H09, H14, M07) vẫn không gọi tool thừa.

Còn lại — tất cả là ranh giới capability/argument convention → sửa `tools.yaml` ở v2:

```text
Case: H12_confirm_before_ticket, M05_ticket_confirmation
Actual calls: create_ticket(confirmed=false, ...) → tool trả needs_confirmation (guardrail lớp 2 hoạt động)
Observed mismatch: model dùng confirmed=false như "dry-run" để xin xác nhận, thay vì clarify(yes_no)
Giả thuyết: declaration create_ticket ("Tạo một ticket hỗ trợ.") không nói gọi nó là hành động ghi và chỉ được gọi SAU xác nhận
Artifact: tools.yaml (create_ticket + clarify)

Case: H17_triage_with_three_sources
Actual calls: inspect_device(asset_id=LT-318) — thiếu check=vpn
Giả thuyết: mô tả `check` chỉ ghi "Nhóm kiểm tra"; model để mặc định all dù triệu chứng là VPN
Artifact: tools.yaml (inspect_device.check)

Case: H19_ambiguous_environment
Actual calls: check_service_status(email, staging) cho "môi trường demo của team QA"
Giả thuyết: mô tả `environment` không nói cấm map từ ngoài enum
Artifact: tools.yaml (check_service_status.environment)
```

## v2 — `runs/v2_B_base_gemini_20260914T192322413397.json` (chỉ sửa `tools.yaml`)

case_accuracy 0.867 → **0.933** · routing 0.933 · args 0.933 · 2/30 FAIL. H17, H19, M05 pass.
Regression: M03 (pass ở v1) lại rơi vào pattern A "JSON tường thuật thay vì gọi tool" — cho thấy rule ở v1 chưa đủ mạnh với model lite.

```text
Case: H12_confirm_before_ticket
Actual calls: create_ticket(confirmed=false, ...)
Giả thuyết: với yêu cầu đơn "Tạo ticket ...", model coi lời yêu cầu là xác nhận ngầm. Description tool chưa đủ; cần rule thủ tục trong prompt:
  phản hồi đầu tiên cho mọi yêu cầu tạo ticket LUÔN là clarify(yes_no) kèm payload
Artifact: system_prompt.md

Case: M03_correct_asset
Actual calls: [] — text "Tôi đang kiểm tra thông tin bảo mật cho máy LT-240" + JSON
Giả thuyết: model tường thuật hành động ("đang kiểm tra") thay vì gọi tool; cần cấm rõ câu tường thuật và nói JSON chỉ hợp lệ sau tool result
Artifact: system_prompt.md
```

## v3 — `runs/v3_B_base_gemini_20260914T192613311974.json` (chỉ sửa `system_prompt.md`)

case_accuracy 0.933 → **1.0** · routing 1.0 · args 1.0 · multiturn 1.0 · 30/30 PASS, không regression.

Tổng kết 3 vòng:

| Version | Artifact | case_acc | multiturn | Fix chính |
|---|---|---:|---:|---|
| v0 | baseline | 0.700 | 0.60 | — |
| v1 | system_prompt.md | 0.867 | 0.90 | tool call là hành động; JSON chỉ sau tool result; latest-turn-wins; confirmation gắn payload |
| v2 | tools.yaml | 0.933 | 0.90 | when/when-not cho mỗi tool; convention response_type/check/environment; create_ticket = write action |
| v3 | system_prompt.md | 1.000 | 1.00 | thủ tục ticket: phản hồi đầu = clarify yes/no; cấm tường thuật thay tool call |

Lưu ý: automatic score chỉ chấm tool name + subset args. Chất lượng câu trả lời, tool result error và
an toàn dữ liệu được review thủ công ở group/extension/adversarial (xem REPORT.md B4a, B6).
