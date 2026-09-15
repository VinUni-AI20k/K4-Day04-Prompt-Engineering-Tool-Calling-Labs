# Team members

The rows below combine the team's official course records with merged contribution history.

| Full name | Student ID | GitHub username | Role | Merged evidence |
|---|---|---|---|---|
| Trần Nguyễn Tiến Đức | 2A202602871 | TNTD-dev | Role D, team lead, UI, integration, demo, report | PR #10 and integration commits |
| Hoàng Anh Tài | 2A202602612 | TaiHoang2501 | Role A, prompt behavior | Commit `f7128c7` |
| Nguyễn Việt Thành | 2A202602924 | jansulubituu | Role C, baseline, eval, evidence | PR #9 |
| Nguyễn Anh Dũng | 2A202602554 | anhdungbk | Role B, tool contracts | PR #11 |
| Lê Nguyễn Quốc Bảo | 2A202603011 | lengqbaorr | Role E, security and bonus tool | PR #12 |

## Individual self-reflections

Each member must write their own reflection below and commit it under their own Git identity.
A useful reflection states what they changed, what evidence changed their mind, one limitation, and what they would improve next.

### Role D (Team lead)

Tôi phụ trách điều phối nhóm, tích hợp các nhánh, xây dựng UI streaming và chuẩn bị demo cuối.
Qua quá trình tích hợp, tôi nhận ra một giao diện đẹp chỉ có giá trị khi người xem theo dõi được tool call, arguments, result, lỗi và phản hồi cuối trong cùng một hội thoại.
Tôi đã điều chỉnh UI để phần Working có thể đóng mở, phát lại transcript được ghi nhãn rõ ràng và artifact version được hiển thị gọn để đối chiếu evidence.
Hạn chế hiện tại là một số action boundary vẫn cần runtime state thay vì chỉ dựa vào prompt.
Nếu phát triển tiếp, tôi sẽ bổ sung state machine phía server để gắn confirmation với chính xác action payload trước khi cho phép ghi dữ liệu.

### Role A

Tôi phụ trách cải thiện system prompt từ các failure của baseline v0.
Tôi bổ sung quy tắc xử lý identifier còn thiếu, correction, cancellation, latest intent, confirmation và nội dung không đáng tin cậy mà không hard-code theo case ID.
Kết quả v1 tăng case accuracy từ 0.7000 lên 0.9000 với 30/30 case được đo và không có provider error, cho thấy các quy tắc tổng quát đã cải thiện routing và action boundary.
Hạn chế là prompt vẫn không thể bảo đảm tuyệt đối trước role spoofing hoặc confirmation cũ trong mọi adversarial case.
Nếu làm tiếp, tôi sẽ phối hợp với phần runtime để xác thực nguồn của message và buộc confirmation gắn với payload chuẩn hóa.

### Role B

Tôi phụ trách hoàn thiện tool schema và mô tả ranh giới trách nhiệm giữa các tool.
Tôi làm rõ điều kiện sử dụng, trường bắt buộc, kiểu dữ liệu và giới hạn argument để model phân biệt đúng lookup, diagnostic, policy, external search và write action.
Kết quả v2 đạt case accuracy 0.9000 so với baseline 0.7000, đồng thời tạo nền tảng để tích hợp bonus tool `lookup_ticket_status` theo hợp đồng read-only rõ ràng.
Hạn chế là schema chỉ hướng dẫn model và chưa tự ngăn được mọi tool plan không hợp lệ trước khi tool thực thi.
Nếu phát triển tiếp, tôi sẽ thêm lớp validation tập trung cho tool plan và kiểm thử contract tự động giữa YAML schema với Python implementation.

### Role C

Tôi phụ trách chạy baseline, phân loại failure và xây dựng bộ eval riêng của nhóm.
Baseline v0 đạt 21/30 case, từ đó tôi dùng evidence để xác định các vấn đề về wrong tool, missing information và confirmation thay vì sửa theo cảm tính.
Bộ group eval cuối có đúng 10 case gốc gồm 5 single-turn và 5 multi-turn, bao phủ correction, cancellation, context isolation, external boundary và bonus tool.
Hạn chế là điểm số tổng hợp chưa thể hiện đầy đủ mức độ nghiêm trọng khác nhau giữa lỗi routing thông thường và lỗi action boundary.
Nếu làm tiếp, tôi sẽ bổ sung trọng số theo rủi ro và tách safety pass rate thành một metric bắt buộc bên cạnh case accuracy.

### Role E

Tôi phụ trách rà soát data leakage, kiểm tra action boundary và xây dựng bonus tool `lookup_ticket_status`.
Tôi bổ sung guard cho Boolean confirmation, dữ liệu nhạy cảm, identifier nội bộ gửi ra Tavily, official-domain filtering và instruction-like text từ kết quả web.
Các security smoke test xác nhận write action chỉ ghi trong thư mục cô lập khi có Boolean `true`, external request chỉ chứa dữ liệu sản phẩm công khai và bonus tool không thay đổi fixture nguồn.
Hạn chế là model vẫn có thể chọn sai action trong adversarial trace dù implementation và evaluator đã cô lập side effect.
Nếu phát triển tiếp, tôi sẽ đưa authorization ra khỏi prompt, thêm pending-action token và mở rộng adversarial suite cho payload smuggling cùng role spoofing.
