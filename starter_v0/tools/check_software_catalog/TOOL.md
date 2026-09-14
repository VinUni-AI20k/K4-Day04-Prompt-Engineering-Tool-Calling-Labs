---
name: check_software_catalog
track: bonus
kind: local_knowledge
provider: mock_software_catalog
requires_env: []
inputs: [software_name, category]
outputs: [found, software_name, approval_status, approved_version, license_type, policy_notes]
side_effect: false
---
# check_software_catalog

Tra cứu danh mục phần mềm được phê chuẩn của công ty Northstar Labs.
Xác định phần mềm có được phép cài đặt hay không (approved, requires_approval, prohibited).
Đối với các phần mềm bị cấm (prohibited), tool sẽ cảnh báo nghiêm cấm theo chính sách an toàn thông tin.
Các danh mục hỗ trợ: all, communication, developer_tools, security, utilities, prohibited.
