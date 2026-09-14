# Tool: `lookup_ticket_status`

## Summary
Tra cứu tiến độ và trạng thái chi tiết của một ticket hỗ trợ kỹ thuật đã tồn tại bằng Mã Ticket (ví dụ: `INC-1001`).

## Inputs
- `ticket_id` (string, required): Mã ticket cần tra cứu (dạng `INC-xxxx`).

## Behavior & Trust Boundaries
- Đọc từ dữ liệu ticket giả lập local (`helpdesk_data/tickets.json`).
- Không thực hiện thay đổi dữ liệu (Read-only operation).
- Trả về thông tin trạng thái (`open`, `in_progress`, `resolved`), mức ưu tiên, người xử lý (`assigned_to`) và thời gian cập nhật.
