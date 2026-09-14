---
name: diagnose_network
track: bonus
kind: local_status
provider: mock_network_monitor
requires_env: []
inputs: [target, check_type]
outputs: [target, node_name, ping_ms, packet_loss_pct, dns_status, gateway_status, status]
side_effect: false
---
# diagnose_network

Kiểm tra trạng thái kết nối mạng và chẩn đoán độ trễ, mất gói, DNS, gateway cho các văn phòng chi nhánh và gateway nội bộ.
Không thực hiện lệnh shell hệ điều hành trực tiếp; từ chối các chuỗi ký tự nguy hiểm có nguy cơ command injection.
Các target hợp lệ gồm: office_hanoi, office_hcm, office_danang, gateway_vpn, dns_primary, server_sso.
Các kiểu kiểm tra hỗ trợ: all, ping, packet_loss, dns, gateway.
