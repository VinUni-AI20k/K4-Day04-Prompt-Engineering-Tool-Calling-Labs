---
name: lookup_ticket_status
track: bonus
kind: query
provider: local_ticket_store
requires_env: []
inputs: [ticket_id]
outputs: [status, ticket]
side_effect: none
requires_confirmation: false
---
# lookup_ticket_status

Tra cứu trạng thái, mức độ ưu tiên, tóm tắt sự cố và tiến độ xử lý của một IT ticket đã có dựa vào `ticket_id` (định dạng chuẩn: `LAB-XXXXXXXX`).

Tool ưu tiên kiểm tra các ticket mới tạo trong thư mục `tickets/`, sau đó tra cứu trong database giả lập `helpdesk_data/mock_tickets.json`. Tool áp dụng rào chắn bảo mật regex nghiêm ngặt (`^LAB-[A-F0-9]{8}$`) để triệt tiêu nguy cơ Path Traversal hoặc tấn công chèn mã.
