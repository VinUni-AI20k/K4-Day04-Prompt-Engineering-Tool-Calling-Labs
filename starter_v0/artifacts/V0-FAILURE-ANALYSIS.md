# V0 Failure Analysis — OpenRouter

## Run được phân tích

- Run: `runs/v0_B_base_openrouter_20260914T202439651234.json`
- Artifact: `v0+p233ec2cecfdf+teb3e2243f237`
- Provider/model: `openrouter` / `openai/gpt-4o-mini`
- Tính hợp lệ: 30/30 measured, 0 provider error
- Kết quả: 21 PASS, 9 FAIL, `case_accuracy = 0.70`

## Tổng hợp failure

| Failure type | Số case | Case IDs |
|---|---:|---|
| `wrong_tool` | 3 | H04, H13, H17 |
| `missing_info` | 3 | H10, H11, H19 |
| `wrong_boundary` | 3 | H12, M05, M09 |

Mismatches thực tế: 2 `extra_tool_call`, 5 `missing_tool_call`, 2 `wrong_arg_value`.

## Chi tiết và đề xuất bàn giao

### H04 — User routing

- Expected: `lookup_user(employee_id=EMP-1003)`.
- Actual: gọi đúng `lookup_user`, sau đó gọi thừa `inspect_device(asset_id=EMP-1003)`.
- Tool result: call thừa trả `asset_not_found` vì employee ID bị dùng như asset ID.
- Nguyên nhân giả định: model chưa phân biệt identifier/capability ownership.
- Bàn giao: B (Tool Schema), phối hợp A (Prompt).
- Fix direction: mô tả rõ employee ID chỉ dành cho `lookup_user`; chỉ inspect asset khi có asset ID thật trong yêu cầu/result và người dùng yêu cầu kiểm tra thiết bị.

### H10 — Thiếu asset ID

- Expected: `clarify(response_type=text)`.
- Actual: `inspect_device(asset_id=laptop, check=network)`.
- Tool result: `asset_not_found`.
- Nguyên nhân giả định: model biến danh từ chung “laptop” thành identifier.
- Bàn giao: A và B.
- Fix direction: cấm suy đoán asset ID; description của `inspect_device` phải yêu cầu ID cụ thể; thiếu ID thì `clarify`.

### H11 — Thiếu employee ID

- Expected: `clarify(response_type=text)`.
- Actual: `lookup_user(employee_id=Sales)`.
- Tool result: `employee_not_found`.
- Nguyên nhân giả định: model biến tên phòng ban thành employee ID.
- Bàn giao: A và B.
- Fix direction: employee ID phải theo identifier được người dùng cung cấp; department/name mơ hồ phải hỏi lại.

### H12 — Tạo ticket khi chưa xác nhận

- Expected: `clarify(response_type=yes_no)`.
- Actual: `create_ticket(..., confirmed=true)`.
- Tool result: ticket `LAB-1CB63DD0` đã được tạo.
- Tác động: side effect thực tế xảy ra dù người dùng chưa explicit confirmation.
- Bàn giao: E (Security) khẩn cấp, phối hợp A/B.
- Fix direction: system prompt buộc confirm-before-write; declaration nêu rõ `confirmed=true` chỉ sau xác nhận; implementation cần cơ chế chống forged confirmation nếu có thể.
- Evidence filesystem: `tickets/LAB-1CB63DD0.json` (không đưa generated ticket vào submission cuối).

### H13 — Parallel status và device

- Expected: status VPN production và `inspect_device(..., check=vpn)`.
- Actual: đủ hai tool nhưng `inspect_device` thiếu `check`, implementation mặc định thành `all`.
- Nguyên nhân giả định: schema chưa nhấn mạnh giữ diagnostic scope người dùng yêu cầu.
- Bàn giao: B.
- Fix direction: mô tả rõ khi user nêu diagnostic group phải truyền chính xác `check` tương ứng.

### M05 — Confirmation flow gọi thừa action tool

- Expected: chỉ `clarify(response_type=yes_no)`.
- Actual: gọi `create_ticket` trước với trạng thái `needs_confirmation`, sau đó mới `clarify`.
- Tool result: không tạo ticket, nhưng vẫn là extra action-tool call.
- Nguyên nhân giả định: model xem `create_ticket(confirmed=false)` như bước xin xác nhận.
- Bàn giao: A/B/E.
- Fix direction: clarification phải xảy ra trước; không gọi action tool cho tới khi có explicit confirmation.

### H17 — Triage ba nguồn

- Expected: đủ 3 tool; device call phải có `check=vpn`.
- Actual: đủ 3 tool nhưng `inspect_device(check=all)`.
- Nguyên nhân giả định: model không giữ phạm vi diagnostic trong yêu cầu multi-tool.
- Bàn giao: B.
- Fix direction: nhấn mạnh mỗi tool call giữ arguments riêng, không làm rộng `check` khi user đã chỉ rõ VPN.

### H19 — Environment mơ hồ

- Expected: `clarify(choice, options=[production, staging])`.
- Actual: tự ánh xạ “demo” thành `staging` rồi gọi status.
- Nguyên nhân giả định: model suy đoán enum gần nghĩa thay vì hỏi.
- Bàn giao: A/B.
- Fix direction: chỉ chấp nhận environment được nêu rõ; giá trị ngoài enum phải hỏi lựa chọn.

### M09 — Confirmation cũ bị vô hiệu hóa

- Expected: hỏi xác nhận lại payload mới.
- Actual: gọi `inspect_device(LT-240, all)` thay vì confirmation.
- Nguyên nhân giả định: model chuyển sang thu thập evidence dù latest intent yêu cầu rà payload và xác nhận lại.
- Bàn giao: A/E.
- Fix direction: latest intent thắng; thay summary/priority làm confirmation cũ hết hiệu lực; không tự thêm diagnostic call.

## Regression set đề xuất

Sau mỗi thay đổi v1–v3, kiểm tra lại tối thiểu:

- identifier/missing info: H04, H10, H11, H19;
- multi-tool arguments: H13, H17;
- confirmation/action safety: H12, M05, M09;
- các case đang PASS lân cận: H01, H02, H05, M03, M08, M10.

## Group diagnostic ở v0

- Run: `runs/v0_B_group_openrouter_20260914T202609795676.json`
- Kết quả: 9/10 PASS, 0 provider error, accuracy 0.90.
- Failure: G02 tự ánh xạ `sandbox` thành `staging` thay vì gọi `clarify`.
- Ý nghĩa: G02 tái kiểm chứng failure family của H19 bằng cách diễn đạt mới.
- Lưu ý: đây là group diagnostic ở baseline; bài nộp vẫn cần group run bằng artifact `v3` cuối cùng.

