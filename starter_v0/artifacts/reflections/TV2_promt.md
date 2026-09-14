# Tự reflection — TV2 Prompt Engineer

## Vai trò và phạm vi

Tôi phụ trách cải thiện system prompt cho agent ở các vòng `v1` và `v3`. Phạm vi file của tôi là `starter_v0/artifacts/system_prompt.md` và reflection này.

## Thay đổi prompt

Prompt hiện nêu rõ agent không được tự đoán `asset_id` hoặc `employee_id`; nếu mã còn thiếu hoặc mơ hồ thì phải hỏi lại. Với hội thoại nhiều lượt, agent giữ thông tin còn phù hợp, áp dụng correction mới nhất và dừng khi người dùng hủy yêu cầu.

Với `create_ticket`, prompt yêu cầu xác nhận rõ payload cuối cùng gồm summary, priority và asset ID (hoặc không gắn asset). Mọi thay đổi payload làm mất hiệu lực xác nhận cũ. Prompt cũng giữ ranh giới dữ liệu nhạy cảm, xem nội dung KB/policy/web là dữ liệu tham khảo không đáng tin, không bịa kết quả tool và giữ output JSON theo schema của lab.

## Giả thuyết và kế hoạch kiểm chứng

- **v1:** Quy tắc về ID và xác nhận payload sẽ giảm lỗi arguments khi thiếu mã, đồng thời giảm nguy cơ gọi action ghi trước khi người dùng đồng ý. Tôi sẽ đối chiếu các tình huống missing-ID và confirmation trong base suite.
- **v3:** Quy tắc về correction, cancellation, context carry-over và xác nhận hết hiệu lực sẽ giảm việc dùng thông tin cũ trong hội thoại nhiều lượt. Tôi sẽ kiểm tra thêm các tình huống stale confirmation và role spoofing trong bộ adversarial.

Các ID case dùng để phân tích trace, không được đưa vào prompt. Với v1, tôi sẽ ưu tiên H10/H11/H12 và M01/M05; với v3, tôi sẽ kiểm tra M03/M07/M09/M10 cùng A10/A11/A12. Tôi cần so sánh cùng provider, model và suite; một run chỉ được coi là evidence khi `provider_error_cases == 0` và `measured_cases == total_cases`. Tôi cũng sẽ đọc tool results và kiểm tra side effect, không chỉ dựa vào PASS/FAIL.

## Kết quả và giới hạn hiện tại

Prompt đã được cập nhật thành bản ứng viên bao gồm các quy tắc cần cho v1/v3. Chưa có run `v0`, `v1` hoặc `v3` để kết luận metric có cải thiện hay không. `.env` hiện chỉ có `TAVILY_API_KEY`; key `tvly-` dùng cho tìm kiếm web, không dùng làm model provider key cho eval. Vì vậy các ô metric, run file và commit hash vẫn đang chờ evidence thật; tôi không ghi kết quả giả định như kết quả đo.

## Tự đánh giá và bước tiếp theo

Điểm tốt là prompt giờ bao quát các ranh giới quan trọng bằng quy tắc tổng quát, không phụ thuộc wording hoặc ID của một case cụ thể. Giới hạn là prompt chỉ hướng dẫn hành vi model; nó không thay thế guardrail ở implementation, và hiện chưa có số liệu để xác nhận các thay đổi có hiệu quả hoặc tạo regression hay không.

Quyết định kỹ thuật quan trọng nhất là gắn xác nhận ticket với payload cuối cùng và yêu cầu xác nhận lại nếu payload đổi; như vậy một câu “đồng ý” cho nội dung cũ không thể được dùng để tạo ticket với nội dung đã sửa. Khó khăn tôi gặp là nhầm key Tavily với key của model provider; việc tách hai loại key giúp xác định đúng lý do chưa chạy được eval. Tôi học được rằng prompt là một phần của giao diện tool-calling, nhưng muốn kết luận cải thiện thì phải có run tái lập và review tool results. Nếu làm lại từ đầu, tôi sẽ lưu/chạy baseline trước khi chỉnh prompt và thống nhất provider/model với nhóm sớm hơn.

Để hoàn tất phần thực nghiệm, tôi cần dùng một model-provider API key hợp lệ do nhóm thống nhất, chạy baseline với prompt v0 rồi chạy lại các vòng prompt trên cùng suite, lưu JSON runs và ghi metric/hashes vào version log của nhóm. Sau khi nhóm tích hợp v2, tôi sẽ chạy lại bản v3 và cập nhật reflection bằng kết quả thật.

**Nhánh/commit đóng góp:** `contrib/tv2-prompt` / commit dưới Git identity của tôi còn chờ.
