# Ghi chú cho UI & Report Lead

## A1. Mô tả capability của agent

Northstar Helpdesk Agent hỗ trợ các yêu cầu IT service desk trên dữ liệu giả lập: kiểm tra trạng thái dịch vụ, inspect thiết bị, tra cứu user, tìm KB/policy, format incident report và tạo ticket sau khi có xác nhận rõ ràng. Agent chỉ xử lý trong phạm vi helpdesk, không tự đoán asset ID hoặc employee ID, và bảo vệ dữ liệu nội bộ/secret khỏi các cách dùng tool không an toàn.

## A1. Demo URL

URL Streamlit local:

```text
http://localhost:8501
```

## A2. Danh sách tool

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung thông tin hoặc xin xác nhận rõ ràng | core |
| search_kb | Tìm trong các bài hướng dẫn IT knowledge base local | core |
| check_service_status | Kiểm tra trạng thái dịch vụ dùng chung như VPN, email, SSO, Wi-Fi hoặc printing | core |
| inspect_device | Đọc inventory và diagnostic snapshot của một asset cụ thể | core |
| lookup_user | Tra cứu thông tin directory theo employee ID | core |
| format_incident_report | Format các findings đã thu thập thành incident report | core |
| policy | Tìm trong tài liệu chính sách IT nội bộ | optional built-in |
| create_ticket | Tạo support ticket local sau khi có xác nhận rõ ràng | optional built-in |
| search_device_info | Tìm thông tin công khai về manufacturer/model trên web | optional built-in |

## A3. Câu hỏi mẫu

1. Dịch vụ VPN production hiện có đang gặp sự cố không?
2. Kiểm tra riêng kết nối VPN trên LT-204.
3. VPN trên LT-204 lỗi; kiểm tra cả trạng thái VPN production và máy đó.
4. Tạo ticket mức high cho lỗi VPN trên LT-204 giúp mình.
5. Kiểm tra Wi-Fi trên laptop của mình giúp nhé.

## A4. Kịch bản demo đã thử

| Scenario | Tool trace cần thấy | Version | Transcript dự phòng |
|---|---|---|---|
| Kiểm tra trạng thái VPN production bằng Streamlit UI | check_service_status(service=vpn, environment=production) | v0 | transcripts/ui_20260914T182119000929.transcript.json |
| Kiểm tra diagnostic VPN của LT-204 bằng CLI chat | inspect_device(asset_id=LT-204, check=vpn) | v0 | transcripts/v0_openai_20260914T182247374274.transcript.json |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Kết quả |
|---|---|---|---|---|
| UI turn 1: Kiểm tra trạng thái VPN production | v0 | check_service_status(service=vpn, environment=production) | transcripts/ui_20260914T182119000929.transcript.json | Agent route đúng sang tool kiểm tra trạng thái dịch vụ dùng chung, trả về VPN degraded và dẫn incident INC-1042. |
| CLI chat: Kiểm tra VPN trên LT-204 | v0 | inspect_device(asset_id=LT-204, check=vpn) | transcripts/v0_openai_20260914T182247374274.transcript.json | Agent route đúng sang tool inspect thiết bị với asset LT-204 và phạm vi diagnostic là VPN. |

## C2. Bản nháp self-reflection

### Dang Huu Cuong - 2A202602572

- **Vai trò/phần việc được nhận:** D - UI & Report Lead.
- **Những gì tôi đã thay đổi trong repo chung:** Xây dựng Streamlit UI để demo agent, hiển thị câu trả lời, tool calls, arguments, tool results, status, artifact version và transcript path. Tôi cũng thêm dependency Streamlit vào requirements.
- **File hoặc artifact liên quan:** `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/transcripts/ui_20260914T182119000929.transcript.json`.
- **Commit hash hoặc pull request:** TODO: điền sau khi commit.
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tôi tái sử dụng `run_model_tool_loop` từ `chat.py` để UI, CLI và eval evidence dùng chung cùng một behavior của agent.
- **Khó khăn tôi gặp và cách tôi xử lý:** Report cần evidence dễ kiểm tra, nên tôi hiển thị từng tool round bằng expander và dùng JSON viewer cho tool calls/results.
- **Điều tôi học được từ phần việc này:** UI của agent cần ưu tiên khả năng audit: người review phải thấy rõ tool nào được gọi, arguments nào được truyền và result nào hỗ trợ câu trả lời.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Thêm tab tổng hợp eval metrics và nút export evidence trực tiếp sang format của report.

## File do phần D thay đổi

```text
starter_v0/app.py
starter_v0/requirements.txt
starter_v0/artifacts/UI_REPORT_NOTES.md
starter_v0/transcripts/ui_20260914T182119000929.transcript.json
```
