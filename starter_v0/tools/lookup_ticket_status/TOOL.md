---
name: lookup_ticket_status
track: bonus
kind: local_status
provider: none
requires_env: []
inputs: [ticket_id]
outputs: [ticket_id, status, summary, priority, asset_id, requester_id, assigned_to, created_at, updated_at, resolution_notes]
side_effect: false
requires_confirmation: false
---
# lookup_ticket_status

Tra cứu chi tiết trạng thái, người xử lý, mức độ ưu tiên và tiến trình giải quyết của một ticket sự cố IT dựa trên mã ticket (ví dụ: `INC-1042`, `CHG-221`, `TCK-1001`, hoặc các mã `LAB-xxxx` vừa được tạo).
Tool đọc dữ liệu từ cơ sở dữ liệu ticket nội bộ và thư mục ticket cục bộ `starter_v0/tickets/`.
