# Danh sách thành viên

| STT | Họ và tên | Mã sinh viên | GitHub username | Vai trò |
| ---: | --- | --- | --- | --- |
| 1 | Phạm Hồ Quang Dũng | 2A202602860 | `Paim0n3223` | Phụ trách: Kiểm tra môi trường, compile/smoke/preflight; chạy baseline `v0`; phân loại lỗi và điều phối run `v1`–`v3`. Đầu ra: Run JSON các version, `version_log.csv`, bảng so sánh metric và xác nhận các run có `provider_error_cases = 0`. |
| 2 | Nguyễn Hải Đăng | 2A202602963 | Chưa cung cấp | Phụ trách: Phân tích lỗi routing, thiếu identifier, multi-turn, correction/cancellation và confirmation; cải tiến prompt theo từng hypothesis. Đầu ra: `artifacts/system_prompt.md`, giải thích thay đổi prompt và regression review cho các case đã PASS. |
| 3 | Ngô Gia Quốc | 2A202602757 | Chưa cung cấp | Phụ trách chính: Audit tool name, description, schema và argument convention; đối chiếu implementation/`TOOL.md`; sửa implementation khi cần. Đầu ra: `artifacts/tools.yaml`, bảng mapping capability–tool, smoke test hoặc deterministic test cho lỗi implementation. |
| 4 | Nguyễn Đình Khang | 2A202602584 | `ilkhangnd` | Phụ trách chính: Tổng hợp team eval; chạy extension/adversarial suite; kiểm tra injection, forged confirmation, data leak và external boundary. Đầu ra: `data/eval_group.json` đúng 5 single + 5 multi; phân tích ít nhất 3 security case; adversarial evidence và transcript. |
| 5 | Trần Long Khánh | 2A202602538 | `khanhtrankuri` | Phụ trách chính: Xây UI dùng lại `run_model_tool_loop`; hiển thị đầy đủ trace; tích hợp báo cáo và chuẩn bị demo/fallback. Đầu ra: UI hoạt động, `artifacts/REPORT.md`, 3–5 demo scenario và transcript dự phòng khi provider/network lỗi. |
