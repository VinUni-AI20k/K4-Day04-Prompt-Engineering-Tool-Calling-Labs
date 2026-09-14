---
name: inspect_meeting_room
track: bonus
kind: local_inventory
provider: mock_meeting_room_inventory
requires_env: []
inputs: [room_id, aspect]
outputs: [room_id, name, capacity, equipment, av_status, network_status, known_issues]
side_effect: false
---
# inspect_meeting_room

Tra cứu danh mục thiết bị, hệ thống nghe nhìn (AV), màn hình trình chiếu và trạng thái kỹ thuật của phòng họp.
Hỗ trợ các mã phòng họp như MR-101, MR-102, MR-201, MR-301, MR-401 hoặc tìm theo tên phòng.
Các khía cạnh kiểm tra hỗ trợ: all, equipment, av_status, network, issues.
Không lưu trữ hoặc tiết lộ nội dung cuộc họp nội bộ hay hình ảnh camera.
