# Diff artifact theo từng version

Chỉ `description` thay đổi qua mọi version. Tên tool, type, enum, default và required giữ nguyên byte-for-byte.

## tools.yaml — v0 → v1

### `search_kb.description`

**v0** (30 ký tự)
```
Tìm hướng dẫn hỗ trợ kỹ thuật.
```

**v1** (157 ký tự)
```
Tìm hướng dẫn khắc phục sự cố trong knowledge base nội bộ. Trả về hướng dẫn chung theo chủ đề; không đọc trạng thái thực tế của một thiết bị hay một dịch vụ.
```

### `check_service_status.description`

**v0** (32 ký tự)
```
Kiểm tra trạng thái một dịch vụ.
```

**v1** (118 ký tự)
```
Đọc trạng thái hiện tại của một dịch vụ dùng chung theo môi trường. Không chẩn đoán thiết bị của một nhân viên cụ thể.
```

### `inspect_device.description`

**v0** (41 ký tự)
```
Kiểm tra thông tin và chẩn đoán thiết bị.
```

**v1** (140 ký tự)
```
Đọc snapshot chẩn đoán của đúng một tài sản công ty theo mã tài sản. Không tra cứu nhân viên và không đọc trạng thái của dịch vụ dùng chung.
```

### `inspect_device.asset_id`

**v0** (10 ký tự)
```
Mã tài sản
```

**v1** (123 ký tự)
```
Mã tài sản, định dạng LT-/DT-/MB-/PR-/RM- kèm số, ví dụ LT-204. Không nhận mã nhân viên, tên loại thiết bị hay mô tả chung.
```

### `lookup_user.description`

**v0** (40 ký tự)
```
Tra cứu người dùng trong danh bạ hỗ trợ.
```

**v1** (154 ký tự)
```
Tra cứu đúng một nhân viên trong danh bạ theo mã nhân viên và trả về metadata công việc kèm danh sách tài sản được cấp. Không tự chẩn đoán các tài sản đó.
```

### `lookup_user.employee_id`

**v0** (12 ký tự)
```
Mã nhân viên
```

**v1** (100 ký tự)
```
Mã nhân viên, định dạng EMP- kèm số, ví dụ EMP-1003. Không nhận tên người, phòng ban hay mã tài sản.
```

## tools.yaml — v1 → v2

### `search_kb.category`

**v1** (14 ký tự)
```
Nhóm hướng dẫn
```

**v2** (97 ký tự)
```
Nhóm hướng dẫn, chọn theo chủ đề người dùng hỏi. Chỉ dùng all khi chủ đề không thuộc rõ nhóm nào.
```

### `check_service_status.environment`

**v1** (10 ký tự)
```
Môi trường
```

**v2** (146 ký tự)
```
Môi trường. Chỉ tồn tại production và staging. Không tự map một tên môi trường khác (demo, test, UAT, QA, sandbox) sang một trong hai giá trị này.
```

### `inspect_device.check`

**v1** (13 ký tự)
```
Nhóm kiểm tra
```

**v2** (420 ký tự)
```
Nhóm kiểm tra, chọn theo triệu chứng người dùng nêu: network cho Wi-Fi và kết nối mạng, vpn cho VPN và certificate, security cho mã hoá và khoá máy, hardware cho ổ đĩa và bộ nhớ, software cho ứng dụng và driver. Nếu yêu cầu đã nêu một triệu chứng cụ thể thì vẫn thu hẹp theo triệu chứng đó, kể cả khi mệnh đề sau chỉ nói kiểm tra máy. Chỉ dùng all khi người dùng yêu cầu kiểm tra tổng thể hoặc không nêu triệu chứng nào.
```

## tools.yaml — v2 → v4

### `clarify.description`

**v2** (31 ký tự)
```
Gửi một câu hỏi cho người dùng.
```

**v4** (431 ký tự)
```
Hỏi lại người dùng một câu và dừng cho tới lượt sau. Đây là tool phải dùng trong hai tình huống: (1) một giá trị bắt buộc còn thiếu hoặc mơ hồ - mã tài sản, mã nhân viên, môi trường - và người dùng chưa cung cấp ở lượt nào; (2) cần sự đồng ý rõ ràng của người dùng trước một hành động ghi. Trong hai tình huống đó, clarify là tool duy nhất được gọi; không gọi tool dữ liệu với giá trị phỏng đoán và không gọi tool ghi để xem trước.
```

### `clarify.question`

**v2** (7 ký tự)
```
Câu hỏi
```

**v4** (103 ký tự)
```
Câu hỏi. Khi xin xác nhận cho hành động ghi, nêu lại đầy đủ payload sẽ được ghi ngay trong câu hỏi này.
```

### `clarify.response_type`

**v2** (12 ký tự)
```
Kiểu trả lời
```

**v4** (162 ký tự)
```
yes_no khi xin xác nhận một hành động. choice khi giá trị còn thiếu thuộc một tập đóng, kèm options. text khi giá trị là tự do, ví dụ mã tài sản hay mã nhân viên.
```

### `clarify.options`

**v2** (12 ký tự)
```
Các lựa chọn
```

**v4** (106 ký tự)
```
Các lựa chọn, bắt buộc khi response_type là choice. Liệt kê đúng các giá trị hợp lệ của tham số còn thiếu.
```

### `check_service_status.environment`

**v2** (146 ký tự)
```
Môi trường. Chỉ tồn tại production và staging. Không tự map một tên môi trường khác (demo, test, UAT, QA, sandbox) sang một trong hai giá trị này.
```

**v4** (282 ký tự)
```
Môi trường. Chỉ tồn tại production và staging. Không tự map một tên môi trường khác (demo, test, UAT, QA, sandbox) sang một trong hai giá trị này và cũng không rơi về giá trị mặc định trong trường hợp đó; hãy gọi clarify với response_type choice và options là production và staging.
```

### `inspect_device.asset_id`

**v2** (123 ký tự)
```
Mã tài sản, định dạng LT-/DT-/MB-/PR-/RM- kèm số, ví dụ LT-204. Không nhận mã nhân viên, tên loại thiết bị hay mô tả chung.
```

**v4** (253 ký tự)
```
Mã tài sản đầy đủ, định dạng LT-/DT-/MB-/PR-/RM- kèm số, ví dụ LT-204. Không nhận mã nhân viên, tên loại thiết bị hay mô tả chung. Không gửi giá trị giữ chỗ, chuỗi rỗng hay chỉ riêng tiền tố; nếu chưa biết mã đầy đủ thì gọi clarify thay vì gọi tool này.
```

### `lookup_user.employee_id`

**v2** (100 ký tự)
```
Mã nhân viên, định dạng EMP- kèm số, ví dụ EMP-1003. Không nhận tên người, phòng ban hay mã tài sản.
```

**v4** (218 ký tự)
```
Mã nhân viên đầy đủ, định dạng EMP- kèm số, ví dụ EMP-1003. Không nhận tên người, phòng ban hay mã tài sản. Không gửi giá trị giữ chỗ hay chỉ riêng tiền tố; nếu chưa biết mã đầy đủ thì gọi clarify thay vì gọi tool này.
```
