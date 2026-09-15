---
name: check_software_catalog
track: bonus
kind: local_knowledge
provider: mock_software_catalog
requires_env: []
inputs: [software_name, platform]
outputs: [software_name, status, category, license_type, supported_platforms, install_source, notes]
side_effect: false
---
# check_software_catalog

Tra cứu danh mục phần mềm được phê duyệt, phần mềm cần phê duyệt và phần mềm bị cấm trong tổ chức.

## Chức năng
- Kiểm tra trạng thái cấp phép và sử dụng của một phần mềm cụ thể (ví dụ: Docker Desktop, Visual Studio Code, Zoom, Wireshark, BitTorrent).
- Xác định trạng thái sử dụng:
  - `approved`: Được phép cài đặt và sử dụng rộng rãi thông qua Company Portal / Self-Service.
  - `requires_approval`: Cần tạo ticket xin phê duyệt từ quản lý hoặc đội ngũ Security trước khi cài đặt.
  - `prohibited`: Nghiêm cấm cài đặt trên mọi thiết bị của công ty theo chính sách an toàn thông tin.
- Hỗ trợ lọc theo hệ điều hành (`windows`, `macos`, `linux`, hoặc `all`).
- Read-only tool: Không thay đổi hệ thống hoặc thực hiện cài đặt thực tế.

## Ranh giới an toàn & Phân định
- Chỉ tra cứu danh mục quy chuẩn nội bộ; không gọi external search web.
- Phân biệt với `inspect_device`: `inspect_device` kiểm tra phần mềm đang cài trên một asset ID cụ thể; `check_software_catalog` tra cứu chính sách và quy chuẩn chung cho phần mềm trong toàn công ty.
