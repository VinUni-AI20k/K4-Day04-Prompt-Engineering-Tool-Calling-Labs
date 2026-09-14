# Phân nhóm phiên bản theo yêu cầu đã chốt

Trạng thái hiện tại: chỉ thực hiện **v1 — Routing**. Chưa thực hiện v2/v3;
chờ người dùng yêu cầu riêng. Case 6 và Case 7 trong danh sách ghi chú ban đầu
thuộc bạn B, không chỉnh các phần đó.

| Phiên bản | Phạm vi | Case eval liên quan |
|---|---|---|
| v1 — Routing | Phân biệt shared service, asset diagnostic, hướng dẫn KB và directory; gọi đủ nguồn được yêu cầu | H01–H04; phần chọn tool của H13, H15–H18 |
| v2 — Arguments | Chuẩn hóa và trích xuất check, category, environment; các tham số cụ thể | H05, H06; phần arguments của H03, H13, H15–H18 |
| v3 — Context & Clarify | Thiếu ID/thông tin gọi clarify; carry-over, correction, cancellation; đổi template báo cáo | H07, H10, H11, H19, H20; M01–M10 |
| Nhóm xác nhận/an toàn, để sau | Xác nhận action và payload thay đổi; chưa tối ưu trong v1 | H12, M05, M09; adversarial suite |
| Kiểm tra hồi quy phạm vi | Ngoài helpdesk, câu hỏi về năng lực | H08, H09, H14 |

Các case có nhiều khía cạnh được phân theo **loại lỗi**, không sửa tất cả hành
vi trong một case chỉ vì case đó có phần routing. Ví dụ H13/H17 chọn đủ tool
thuộc v1, còn `check=vpn` thuộc v2. H19 chọn production/staging khi đã rõ thuộc
arguments; hỏi lại khi demo/QA mơ hồ thuộc v3.

Đối chiếu danh sách ghi chú ban đầu:

- Case 1: phân biệt lookup_user và inspect_device thuộc v1; format ID và hỏi
  lại khi thiếu ID để v2/v3. Khi triển khai phần đó, LT áp dụng cho laptop;
  vẫn giữ EMP lookup và asset DT/PR theo xác nhận của người dùng.
- Case 2 và 9 (M09): xét lượt cuối và ngữ cảnh thuộc v3.
- Case 3: thiếu thông tin gọi clarify thuộc v3.
- Case 4: xác nhận action để nhóm context/clarify và an toàn, không sửa ở v1.
- Case 5 và 8 (H19): hỏi rõ service/environment mơ hồ thuộc v3.
- Case 6: check trong tools.yaml thuộc v2, bạn B phụ trách.
- Case 7 (H17): bỏ query khỏi required do bạn B phụ trách; không sửa ở đây.

## Quy tắc lưu evidence

Các run trước khi chốt phân nhóm đã trộn routing, arguments và context.
Chúng được giữ nguyên trong `evidence/v1/` để truy vết lịch sử, nhưng **không
phải evidence cho v1 Routing**. Bảng log cũ được lưu riêng tại
`evidence/v1/mixed-scope-version-log.csv`. Không dùng kết quả 30/30 cũ để báo
điểm cho bản chỉ routing hiện tại.

Schema hiện tại giữ nguyên toàn bộ parameters của baseline; chỉ sửa description
của bốn tool routing. Prompt hiện tại chỉ thêm hướng dẫn phân định bốn tool.
