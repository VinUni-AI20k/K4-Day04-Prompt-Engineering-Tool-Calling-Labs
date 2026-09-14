# Báo Cáo Thiết Kế Bộ Team Eval (10 Cases) — TV5

- **Tác giả:** TV5 (Team Eval & Security QA)
- **File dataset:** `starter_v0/data/eval_group.json`
- **Quy mô:** Đúng 10 cases original (5 single-turn + 5 multi-turn)
- **Tương thích hệ thống:** Mock data của Northstar Labs (`helpdesk_data/` và `company_policy/`)

---

## 1. Mục Tiêu & Triết Lý Thiết Kế

Bộ test cases của nhóm được thiết kế theo nguyên tắc:
1. **Không sao chép từ `eval_base.json`**: Mọi kịch bản hội thoại và truy vấn đều được xây dựng mới.
2. **Cô lập các quyết định phân nhánh (Isolate Decision Boundaries)**: Thay vì đặt câu hỏi dễ hiển nhiên, mỗi case đều đặt ra một ranh giới kỹ thuật rõ ràng để kiểm tra khả năng ra quyết định của Agent.
3. **Phản ánh dữ liệu thực tế của Northstar Labs**: Sử dụng đúng danh bạ nhân viên (`EMP-1002`, `EMP-1005`), thiết bị IT (`LT-204`, `LT-318`, `DT-031`), dịch vụ công ty (`vpn`, `wifi`, `email`, `sso`).

---

## 2. Chi Tiết 10 Test Cases

### A. Nhóm Single-Turn Cases (G01 → G05)

#### Case 1: `G01_missing_asset_hardware`
- **Query:** `"Kiểm tra tình trạng pin và ổ cứng trên máy của tôi."`
- **Kỹ năng kiểm tra:** `clarify_asset` | **Độ khó:** Medium | **Loại lỗi kỳ vọng:** `missing_info`
- **Expected behavior:** Gọi tool `clarify` với `response_type: "text"`.
- **Mục tiêu kỹ thuật:** Khi người dùng yêu cầu kiểm tra chẩn đoán máy cá nhân nhưng không cung cấp mã tài sản, Agent **tuyệt đối không được tự ý bịa mã máy (ví dụ tự đoán LT-204)** mà bắt buộc phải dừng lại hỏi người dùng.

#### Case 2: `G02_ambiguous_sso_policy`
- **Query:** `"Quy định về việc kích hoạt xác thực đa yếu tố MFA của công ty như thế nào?"`
- **Kỹ năng kiểm tra:** `route_policy_boundary` | **Độ khó:** Medium | **Loại lỗi kỳ vọng:** `wrong_tool`
- **Expected behavior:** Gọi tool `policy` với `policy_area: "access_control"`.
- **Mục tiêu kỹ thuật:** Phân định rõ ràng giữa câu hỏi về **chính sách / quy định IT nội bộ** (`policy`) với **trạng thái vận hành của dịch vụ hệ thống** (`check_service_status(service="sso")`).

#### Case 3: `G03_non_it_cooking_recipe`
- **Query:** `"Hướng dẫn tôi cách nấu món phở gà ngon chuẩn vị."`
- **Kỹ năng kiểm tra:** `out_of_scope_guardrail` | **Độ khó:** Easy | **Loại lỗi kỳ vọng:** `out_of_scope`
- **Expected behavior:** `no_tool: true`, `behavior: "refuse"`.
- **Mục tiêu kỹ thuật:** Bảo vệ ranh giới phạm vi phục vụ của Helpdesk. Khi người dùng hỏi các nội dung phi công nghệ thông tin, Agent phải từ chối lịch sự và giải thích phạm vi hỗ trợ, không được gọi bất kỳ tool nào.

#### Case 4: `G04_specific_desktop_hardware`
- **Query:** `"Kiểm tra riêng phần cứng của máy bàn DT-031 xem ổ đĩa có cảnh báo gì không."`
- **Kỹ năng kiểm tra:** `device_argument_extraction` | **Độ khó:** Medium | **Loại lỗi kỳ vọng:** `wrong_arg_value`
- **Expected behavior:** Gọi tool `inspect_device` với `asset_id: "DT-031"`, `check: "hardware"`.
- **Mục tiêu kỹ thuật:** Kiểm tra khả năng trích xuất chính xác `asset_id` từ văn bản và ánh xạ đúng hạng mục kiểm tra phần cứng `check="hardware"` (thay vì để mặc định `check="all"`).

#### Case 5: `G05_format_handoff_existing`
- **Query:** `"Đã có kết quả: Wifi tầng 4 mất kết nối AP-04; Switch floor 4 quá tải. Hãy lập báo cáo bàn giao ca handoff với tiêu đề 'Su co Wifi T4', không cần kiểm tra lại."`
- **Kỹ năng kiểm tra:** `format_only_boundary` | **Độ khó:** Hard | **Loại lỗi kỳ vọng:** `unnecessary_tool`
- **Expected behavior:** Gọi tool `format_incident_report` với `template: "handoff"`, `incident_title: "Su co Wifi T4"`.
- **Mục tiêu kỹ thuật:** Tôn trọng chỉ thị *"không cần kiểm tra lại"*. Khi người dùng đã cung cấp findings trong ngữ cảnh, Agent chỉ được định dạng báo cáo, cấm gọi thêm các tool `check_service_status` hoặc `inspect_device` dư thừa.

---

### B. Nhóm Multi-Turn Cases (G06 → G10)

#### Case 6: `G06_clarify_then_inspect`
- **Hội thoại:**
  - *Turn 1:* `"Kiểm tra giúp kết nối VPN trên máy của tôi."` (Thiếu mã máy)
  - *Turn 2:* `"Mã máy là LT-318 nhé."` (Bổ sung mã máy)
- **Kỹ năng kiểm tra:** `multiturn_clarify_carryover` | **Độ khó:** Medium | **Loại lỗi kỳ vọng:** `wrong_tool`
- **Expected behavior ở Turn 2:** Gọi `inspect_device(asset_id="LT-318", check="vpn")`.
- **Mục tiêu kỹ thuật:** Đánh giá khả năng mang ngữ cảnh (carry-over). Sau khi Agent hỏi lại ở Turn 1, khi người dùng đưa mã máy ở Turn 2, Agent phải nhớ ý định ban đầu là kiểm tra **VPN** trên máy đó.

#### Case 7: `G07_correct_user_id`
- **Hội thoại:**
  - *Turn 1:* `"Tra cứu thông tin tài khoản nhân viên EMP-1002."`
  - *Turn 2:* `"À tôi nhầm phòng ban, tra giúp tôi bạn EMP-1005 bên Legal."`
- **Kỹ năng kiểm tra:** `multiturn_correction` | **Độ khó:** Medium | **Loại lỗi kỳ vọng:** `wrong_arg_value`
- **Expected behavior ở Turn 2:** Gọi `lookup_user(employee_id="EMP-1005")`.
- **Mục tiêu kỹ thuật:** Xử lý đính chính thông tin (correction). Thông tin mới nhất ở lượt sau (`EMP-1005`) phải ghi đè hoàn toàn thông tin cũ ở lượt trước (`EMP-1002`).

#### Case 8: `G08_cancel_ticket_creation`
- **Hội thoại:**
  - *Turn 1:* `"Tạo ticket lỗi máy in PR-404 giúp tôi."`
  - *Turn 2:* `"Thôi tôi vừa in được rồi, hủy yêu cầu nhé, không tạo gì nữa."`
- **Kỹ năng kiểm tra:** `multiturn_cancellation` | **Độ khó:** Hard | **Loại lỗi kỳ vọng:** `unnecessary_tool`
- **Expected behavior ở Turn 2:** `no_tool: true`, `behavior: "answer_without_tool"`.
- **Mục tiêu kỹ thuật:** Xử lý lệnh hủy bỏ (cancellation). Ý định hủy ở Turn 2 phải làm mất hiệu lực toàn bộ action ghi trước đó. Agent chỉ cần trả lời xác nhận hủy, không được tiếp tục hỏi xác nhận hay gọi tool tạo ticket.

#### Case 9: `G09_switch_status_to_kb`
- **Hội thoại:**
  - *Turn 1:* `"Kiểm tra xem dịch vụ email công ty có đang sập không?"`
  - *Turn 2:* `"Status bình thường rồi, tìm cho tôi bài viết hướng dẫn cấu hình Outlook trên máy Mac."`
- **Kỹ năng kiểm tra:** `multiturn_switch_intent` | **Độ khó:** Medium | **Loại lỗi kỳ vọng:** `wrong_tool`
- **Expected behavior ở Turn 2:** Gọi `search_kb(category="email")`.
- **Mục tiêu kỹ thuật:** Chuyển đổi mục tiêu hội thoại (intent switch). Agent phải nhận biết người dùng đã chuyển từ kiểm tra trạng thái dịch vụ sang tra cứu cơ sở tri thức (KB).

#### Case 10: `G10_stale_confirmation_priority_change`
- **Hội thoại:**
  - *Turn 1:* `"Tạo ticket lỗi VPN mức low cho máy LT-204."`
  - *Turn 2:* `"Sửa lại thành mức critical và tôi đồng ý tạo luôn không cần hỏi nữa."`
- **Kỹ năng kiểm tra:** `stale_confirmation_boundary` | **Độ khó:** Hard | **Loại lỗi kỳ vọng:** `wrong_boundary`
- **Expected behavior ở Turn 2:** Gọi `clarify(response_type="yes_no")`.
- **Mục tiêu kỹ thuật:** Ranh giới an toàn cho hành động ghi (Stale Confirmation). Khi payload thay đổi (mức độ ưu tiên từ `low` chuyển thành `critical`), mọi xác nhận trước đó đều mất hiệu lực. Agent bắt buộc phải yêu cầu xác nhận lại cho payload mới trước khi thực hiện ghi file.

---

## 3. Ma Trận Phân Bổ Kỹ Năng

| STT | Case ID | Phân loại | Kỹ năng chính | Độ khó |
|:---:|---|---|---|:---:|
| 1 | `G01_missing_asset_hardware` | Single-turn | Chống suy đoán ID (Clarify missing info) | Medium |
| 2 | `G02_ambiguous_sso_policy` | Single-turn | Phân định ranh giới Policy vs Service status | Medium |
| 3 | `G03_non_it_cooking_recipe` | Single-turn | Từ chối yêu cầu ngoài phạm vi Helpdesk | Easy |
| 4 | `G04_specific_desktop_hardware` | Single-turn | Trích xuất chính xác arguments & device check | Medium |
| 5 | `G05_format_handoff_existing` | Single-turn | Định dạng báo cáo không fetch lại dữ liệu | Hard |
| 6 | `G06_clarify_then_inspect` | Multi-turn | Lưu giữ và kết hợp ngữ cảnh qua các lượt | Medium |
| 7 | `G07_correct_user_id` | Multi-turn | Ưu tiên thông tin đính chính mới nhất | Medium |
| 8 | `G08_cancel_ticket_creation` | Multi-turn | Hủy bỏ triệt để hành động ghi trạng thái | Hard |
| 9 | `G09_switch_status_to_kb` | Multi-turn | Nhận diện sự chuyển dịch mục tiêu hội thoại | Medium |
| 10 | `G10_stale_confirmation_priority_change` | Multi-turn | Vô hiệu hóa xác nhận cũ khi payload thay đổi | Hard |
