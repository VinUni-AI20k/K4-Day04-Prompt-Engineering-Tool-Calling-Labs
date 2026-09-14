---
name: lookup_ticket_status
track: bonus
kind: local_status
provider: local_ticket_store
requires_env: []
inputs: [ticket_id]
outputs: [ticket_id, summary, priority, status, assigned_to, created_at, updated_at]
side_effect: false
---
# lookup_ticket_status

Tra cứu thông tin, tiến độ và trạng thái xử lý của ticket hỗ trợ kỹ thuật theo mã ticket (ví dụ: LAB-xxxxxxxx hoặc INC-xxxx).
Kiểm tra cả các ticket vừa được tạo trong thư mục `tickets/` và các ticket lịch sử trong cơ sở dữ liệu.
Áp dụng cơ chế bảo mật: từ chối các ký tự path traversal (../) và tự động che giấu các thông tin nhạy cảm nếu có trong ticket cũ.
