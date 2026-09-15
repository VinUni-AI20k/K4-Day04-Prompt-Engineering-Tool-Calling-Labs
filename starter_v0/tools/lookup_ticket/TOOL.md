---
name: lookup_ticket
track: bonus
kind: local_status
provider: mock_helpdesk_tickets
requires_env: []
inputs: [ticket_id]
outputs: [ticket_id, status, summary, priority, asset_id, assignee_id, requester_id, created_at, updated_at, notes]
side_effect: false
---
# lookup_ticket

Tra cứu trạng thái và thông tin chi tiết của một ticket hỗ trợ kỹ thuật theo mã định danh `ticket_id`.

## Chức năng
- Kiểm tra cả ticket được tạo cục bộ (trong thư mục `starter_v0/tickets/`) lẫn các ticket giả lập được lưu sẵn trong `helpdesk_data/tickets.json`.
- Trả về chi tiết: trạng thái xử lý (`open`, `in_progress`, `resolved`, `closed`), mức độ ưu tiên, người yêu cầu, người được phân công xử lý và ghi chú tiến độ.
- Read-only tool: Không tạo ra side effect hay thay đổi trạng thái ticket.

## Ranh giới an toàn & Validation
- Bắt buộc kiểm tra định dạng `ticket_id` theo mẫu `LAB-[A-F0-9]{8}` hoặc `INC-\d{4}`.
- Chặn các nỗ lực path traversal (ví dụ `../`).
- Trả về lỗi `not_found` rõ ràng khi không tìm thấy ticket thay vì tự đoán hoặc bịa dữ liệu.
