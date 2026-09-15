# v3 — enum boundaries (tools.yaml) + clarify (system_prompt.md)

- Runs: `evidence/runs/v3_B_base_openai_20260914T193512918306.json`,
  `evidence/runs/v3_B_extension_openai_20260914T193535607469.json`
- Artifact version: `v3+p60242d8c7b9b+tabdbd9b3e355`
- Provider/model: `openai` / `gpt-4o-mini`
- Người thực hiện: B bàn giao phần `tools.yaml`, A thực hiện cả hai artifact.

## Hypothesis

Nếu mô tả rõ từng giá trị enum thuộc phạm vi nào, và prompt cấm suy ra
identifier từ mô tả chung đồng thời bắt buộc đặt `response_type`, thì H03, H10
và 4 case policy của extension sẽ PASS mà không làm agent hỏi lại ở các lookup
đã đủ thông tin.

## Kết quả

| Metric | v0 | v1 | v2 | **v3** |
|---|---:|---:|---:|---:|
| case_accuracy (base) | 0.70 | 0.80 | 0.90 | **0.9333** |
| tool_routing_accuracy | 0.7667 | 0.8333 | 0.9667 | **0.9667** |
| argument_accuracy | 0.70 | 0.80 | 0.90 | **0.9333** |
| multiturn_accuracy | 0.80 | 0.80 | 1.00 | **1.00** |
| case_accuracy (extension) | — | — | 0.60 | **1.00** |
| provider_error_cases | 0 | 0 | 0 | 0 |

Base 28/30, extension **10/10**.

## Thay đổi

### `tools.yaml` — ranh giới enum

`search_kb.category` và `policy.policy_area` trước chỉ ghi "Nhóm hướng dẫn" và
"Nhóm chính sách". Model không có cách nào biết mỗi giá trị bao gồm gì, nên mặc
định chọn `all`.

Đã mô tả từng giá trị theo phạm vi nội dung thật:

- `category`: phân nhóm theo **dịch vụ** mà bài hướng dẫn nói tới, không theo từ
  ngữ trong câu hỏi — nêu rõ "profile" của Outlook thuộc `email`, không phải
  `account`.
- `policy_area`: mỗi giá trị ánh xạ tới một văn bản trong `company_policy/`, mô
  tả đúng nội dung văn bản đó.

Thêm ranh giới giữa hai tool ở phần description: `search_kb` cho hướng dẫn khắc
phục sự cố, `policy` cho quy định được/không được làm gì.

Kết quả: **H03 PASS**, và toàn bộ 4 case policy của extension (E01, E02, E03,
E06) PASS — extension từ 0.60 lên 1.00.

### `system_prompt.md` — mục Missing information

Identifier do user cung cấp, không suy ra. Mô tả một vật không phải là mã của
nó: "laptop của mình", tên người, tên phòng ban, chức danh đều để mã ở trạng
thái chưa biết. Tương tự với giá trị ngoài enum đã khai báo.

Kèm quy tắc `response_type`: `text` khi cần user cung cấp giá trị, `choice` khi
tập giá trị hợp lệ cố định, `yes_no` **chỉ** khi xin phê duyệt write action.

## Hai vòng sửa giữa chừng

### Vòng 1 — placeholder bị copy nguyên văn

Sau khi sửa enum, **H10 vốn PASS ở v2 lại FAIL**:

| Case | v2 | v3 lần đầu |
|---|---|---|
| H10 | `clarify(response_type="text")` | `inspect_device(asset_id="LT-xxx")` |
| H11 | `clarify` (thiếu response_type) | `lookup_user(employee_id="EMP-xxxx")` |

Nguyên nhân trớ trêu: B thêm ví dụ định dạng `LT-xxx`, `EMP-xxxx` vào
description để **chống** nhét sai kiểu, nhưng model lấy chính chuỗi placeholder
đó làm giá trị. Một biện pháp phòng thủ tạo ra lỗi mới.

Đã sửa: giữ thông tin định dạng nhưng diễn đạt bằng lời ("gồm tiền tố LT, DT,
MB, PR hoặc RM kèm dấu gạch nối và các chữ số, ví dụ LT-204"), và nói rõ nếu
người dùng chưa nêu mã thì KHÔNG tự tạo giá trị, KHÔNG điền chuỗi mẫu.

Sau sửa: H10 và H11 gọi đúng `clarify` thay vì bịa ID.

### Vòng 2 — clarify quá tay, H02 vỡ

Thêm mục Missing information vào prompt làm H10 PASS nhưng **H02 vỡ**:

- Query: "Kiểm tra tổng thể laptop LT-204 giúp mình." — đã có đủ mã tài sản.
- Actual: `clarify(question="Bạn có xác nhận muốn kiểm tra tổng thể laptop
  LT-204 không?", response_type="yes_no")`

Agent xin **xác nhận cho một thao tác chỉ đọc** — nó nhầm lẫn giữa đọc và ghi.
Đây đúng là rủi ro regression đã ghi trong `v0_failure_analysis.md`: "luật
clarify quá rộng có thể khiến agent hỏi lại ở những case đã đủ thông tin".

Đã sửa bằng cách thu hẹp: `yes_no` **chỉ** dùng cho write action, và thêm câu
"Ask only when something is actually missing. A read-only lookup whose arguments
are all present needs no permission: run it. Never ask the user to confirm a
lookup."

Sau sửa: H02 hồi phục, `case_accuracy` 0.90 → 0.9333.

## Bằng chứng an toàn

`create_ticket` chỉ được gọi ở E05 và E08 — hai case user **thực sự xác nhận** —
và cả hai đều `confirmed=true` hợp lệ. Base suite 30 case: **0 ticket trái
phép**, giữ nguyên kết quả của v2.

## Hai case còn lại

### H11_missing_employee — `wrong_arg_value`

- Expected `clarify {"response_type": "text"}`
- Actual `clarify {"question": "Vui lòng cung cấp mã nhân viên (ví dụ:
  EMP-1003) để tôi có thể kiểm tra tài khoản."}`

**Hành vi đã đúng**: agent hỏi lại đúng thứ cần hỏi thay vì bịa `"Sales"` như
v0/v1. Chỉ thiếu `response_type` dù prompt đã yêu cầu đặt. Đây là giới hạn của
model ở mức nhất quán argument, không phải lỗi thiết kế prompt — H10 cùng cấu
trúc thì đặt đúng.

### H19_ambiguous_environment — `missing_tool_call`

- "Kiểm tra email ở môi trường **demo** của team QA."
- Expected `clarify {"response_type": "choice", "options": ["production",
  "staging"]}`
- Actual `check_service_status {"environment": "staging"}`

Case duy nhất còn sai **hành vi**, và là case bền bỉ nhất — sai giống hệt nhau ở
cả bốn version. Prompt đã nói rõ giá trị ngoài enum phải hỏi lại, `tools.yaml`
đã nói `staging` chỉ dùng khi người dùng chỉ định rõ, nhưng model vẫn coi "demo"
đủ gần với `staging`.

Ở thời điểm v3, đây được ghi là giới hạn thực sự: thêm luật mạnh hơn nữa có
nguy cơ tái tạo regression H02 — agent hỏi lại ở những case environment vốn suy
ra hợp lệ (H06, M02 đang PASS).

> **Cập nhật sau v4:** kết luận này chưa đủ sâu. H19 sửa được, nhưng không phải
> bằng một luật clarify mạnh hơn trong prompt — mà bằng một dòng mô tả ngay tại
> `check_service_status.environment` liệt kê các tên không hợp lệ. Xem
> `v4_review.md`.

## Trạng thái các suite

| Suite | v3 |
|---|---|
| base (30) | 28/30 — 0.9333 |
| extension (10) | 10/10 — 1.00 |
| group (10) | chưa chạy, C đang viết case |
| adversarial (12) | chưa chạy |

Việc còn lại: chạy group khi C nộp `eval_group.json`, và chạy adversarial suite
kèm review thủ công `tickets/` và external request body.
