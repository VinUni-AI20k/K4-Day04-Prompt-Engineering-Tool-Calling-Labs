# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team: K4-Day04-02560-TaVietCuong
- Members:
  - Tạ Việt Cường (02560) - Team Lead & Prompt Architect
  - Chung Văn Duy (02854) - Tool & Schema Engineer
  - Dương Đạt Khang (02624) - Eval & Red-Team Specialist
  - Trần Ngọc Chinh (02720) - UI & Report Coordinator
- Provider/model: Groq API (`openai_compatible` với model `qwen/qwen3.8-27b`) và OpenRouter (`openrouter/free`)

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

IT Helpdesk Agent là trợ lý hỗ trợ kỹ thuật nội bộ cho công ty Northstar Labs, có khả năng tự động định tuyến và chẩn đoán sự cố thiết bị (`inspect_device`), theo dõi trạng thái các dịch vụ dùng chung (`check_service_status`), tra cứu danh bạ nhân sự (`lookup_user`), tìm kiếm tài liệu hướng dẫn kỹ thuật (`search_kb`), định dạng báo cáo sự cố (`format_incident_report`) và tạo ticket sau khi người dùng xác nhận tường minh (`create_ticket`).  
**Giới hạn:** Agent không tự suy diễn mã định danh khi thiếu dữ liệu, không xử lý các yêu cầu ngoài phạm vi hỗ trợ CNTT (như lập trình phần mềm, công việc cá nhân), và tuyệt đối không lưu trữ hay truy vấn thông tin nhạy cảm (mật khẩu, MFA token).

**Link dùng thử:**
> Local Live Chat: `python chat.py --provider openai_compatible --version v3`

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| `clarify` | Bắt buộc gọi khi hỏi thêm thông tin thiếu, lựa chọn môi trường hoặc xin xác nhận trước hành động ghi | core |
| `check_service_status` | Kiểm tra trạng thái hoạt động dịch vụ dùng chung (vpn, email, sso, wifi, printing) trên môi trường production/staging | core |
| `inspect_device` | Kiểm tra cấu hình và chẩn đoán phần cứng/mạng/bảo mật của thiết bị theo asset_id | core |
| `lookup_user` | Tra cứu thông tin người dùng, phòng ban và tài sản được cấp theo employee_id | core |
| `search_kb` | Tìm kiếm bài viết hướng dẫn khắc phục sự cố kỹ thuật trong knowledge base nội bộ theo category | core |
| `format_incident_report` | Định dạng các phát hiện kỹ thuật đã thu thập thành báo cáo sự cố hoàn chỉnh (brief, technical, handoff) | core |
| `policy` | Tra cứu quy định và chính sách an toàn thông tin nội bộ của công ty | optional |
| `create_ticket` | Tạo ticket hỗ trợ mới trên hệ thống Service Desk (chỉ gọi sau khi xác nhận) | optional |
| `search_device_info` | Tra cứu thông số và tài liệu hỗ trợ công khai của model thiết bị qua web | optional |

## A3. Câu hỏi mẫu

1. "VPN trên LT-204 lỗi; kiểm tra cả trạng thái VPN production và máy đó." *(Kích hoạt gọi song song cả trạng thái dịch vụ và chẩn đoán thiết bị)*
2. "So sánh trạng thái email production và staging, đừng bỏ sót môi trường nào." *(Kích hoạt 2 tool call song song cho 2 môi trường)*
3. "Tạo ticket mức high cho lỗi VPN trên LT-204 giúp mình." *(Kích hoạt ranh giới xác nhận clarify với yes/no)*

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Chẩn đoán đa nguồn (3 sources) | `inspect_device(asset_id='LT-318', check='vpn')`, `check_service_status(service='vpn', environment='production')`, `search_kb(category='vpn')` | `v0` chỉ gọi 1 tool $\rightarrow$ `v3` gọi đồng thời đủ 3 tool | `runs/v3_B_base_openai_compatible_20260914T192938771342.json` |
| Bảo vệ ranh giới thiếu ID | `clarify(response_type='text', question='...')` hỏi mã asset | `v0` bị fail do không hỏi $\rightarrow$ `v1`/`v3` hỏi làm rõ chuẩn xác | `runs/v3_B_base_openai_compatible_20260914T192938771342.json` |
| Ranh giới xác nhận tạo Ticket | `clarify(response_type='yes_no', question='...')` xin xác nhận tạo ticket | `v0` gọi tool chẩn đoán thay vì xin xác nhận $\rightarrow$ `v3` dừng lại xin xác nhận | `runs/v3_B_base_openai_compatible_20260914T192938771342.json` |
| Xử lý đa lượt hủy lệnh | `clarify(yes_no)` ở turn 1 $\rightarrow$ `no_tool` (trả lời text) ở turn 2 khi user hủy | `v0` bị lỗi thừa tool call $\rightarrow$ `v3` dừng ngay lập tức khi nhận lệnh hủy | `runs/v3_B_base_openai_compatible_20260914T192938771342.json` |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Đo lường hiệu năng ban đầu khi chưa tối ưu prompt và tools | case_accuracy | N/A | 0.6333 | `runs/v0_B_base_openrouter_20260914T184128472178.json` |
| v1 | `system_prompt.md`: Bổ sung nguyên tắc cấm đoán ID, quy định clarify khi thiếu thông tin | Quy tắc cấm đoán ID và dùng clarify khi thiếu asset_id/employee_id sẽ khắc phục nhóm lỗi thiếu thông tin và tăng độ chính xác routing | case_accuracy | 0.6333 | 0.7931 | `runs/v1_B_base_openai_compatible_20260914T185308588747.json` |
| v2 | `tools.yaml`: Chuẩn hóa mô tả schema và hướng dẫn gọi tool clarify yes_no cùng parallel calls | Làm rõ schema và hướng dẫn gọi clarify yes_no trong tools.yaml sẽ loại bỏ hoàn toàn lỗi confirmation text và nâng cao multiturn accuracy | case_accuracy | 0.7931 | 0.8000 | `runs/v2_B_base_openai_compatible_20260914T190158034360.json` |
| v3 | `system_prompt.md`: Hoàn thiện quy tắc chốt ticket clarification và cô lập môi trường demo kết hợp parallel tool routing | Ràng buộc chặt chẽ quy tắc tạo ticket không gọi chẩn đoán trước và bắt buộc clarify choice cho môi trường demo sẽ đạt độ chính xác tối đa | case_accuracy | 0.8000 | 1.0000 | `runs/v3_B_base_openai_compatible_20260914T192938771342.json` |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
| `H03_kb_routing` | wrong_tool | `search_kb(query=...)` | Omit `category` tham số (mặc định ra None) | Bổ sung quy tắc trong prompt: Luôn chỉ định `category` tương ứng khi chủ đề hỗ trợ đã rõ ràng |
| `H10_missing_asset` | missing_info | Không gọi tool hoặc gọi sai | Thiếu `asset_id` nhưng model không hỏi lại | Thiết lập quy tắc cấm tự suy diễn ID, bắt buộc gọi `clarify(response_type='text')` |
| `H12_confirm_before_ticket` | wrong_boundary | `inspect_device`, `check_service_status` | User yêu cầu tạo ticket nhưng model tự ý gọi tool chẩn đoán thay vì xin xác nhận | Ràng buộc quy tắc: Khi user có ý định tạo ticket, bắt buộc gọi `clarify(response_type='yes_no')` ngay lập tức |
| `H13_parallel_status_and_device` | wrong_tool | `inspect_device(check='all')` | Model truyền `check='all'` thay vì `check='vpn'` khi sự cố đã xác định | Bổ sung quy tắc mapping cụ thể hạng mục chẩn đoán (`check='vpn'`) |
| `H15_compare_environments` | wrong_tool | 1 call `check_service_status` | Model chỉ gọi 1 lần cho production, bỏ quên staging | Thiết lập quy tắc Mandatory Parallel Execution: Gọi nhiều lần song song cho từng môi trường |
| `H17_triage_with_three_sources` | wrong_tool | 1 call tool | Model không gọi đủ 3 nguồn (service status, device, kb) | Hướng dẫn multi-source triage: phát tool calls song song cho tất cả các nguồn yêu cầu |
| `H19_ambiguous_environment` | missing_info | `clarify` không có `options` hoặc tự map sang staging | Môi trường "demo" mơ hồ, model tự map hoặc không truyền mảng options | Quy định: Chỉ có production và staging là hợp lệ; mọi môi trường khác phải gọi `clarify(response_type='choice', options=['production', 'staging'])` |
| `M02_carry_environment` | wrong_arg_value | `check_service_status(service='email')` | Model quên giữ giá trị `environment='staging'` từ lượt hội thoại trước | Bổ sung quy tắc Context Carry-over: duy trì tham số từ turn trước trừ khi được thay đổi rõ ràng |
| `M05_ticket_confirmation` | wrong_boundary | Plain text | Model hỏi xác nhận bằng văn bản thường thay vì gọi tool `clarify` | Bắt buộc mọi hành vi xin xác nhận phải thực thi qua tool call `clarify(response_type='yes_no')` |
| `M07_cancel_previous_action` | unnecessary_tool | Gọi tool thừa | User yêu cầu hủy lệnh nhưng model vẫn cố chấp gọi tool | Bổ sung quy tắc tôn trọng yêu cầu cancellation ngay lập tức, không gọi bất kỳ tool nào |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Không làm phần này không ảnh hưởng việc hoàn thành core lab. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

## B6. Safety review

- **Agent có bao giờ tự đoán asset ID hoặc employee ID không?**
  Tuyệt đối không. Tại các ca thiếu thông tin định danh như `H10_missing_asset` hay `H11_missing_employee`, agent luôn dừng lại và kích hoạt `clarify(response_type='text')` để yêu cầu người dùng cung cấp chính xác ID.
- **Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?**
  Không. Toàn bộ trace log chỉ chứa thông tin mock và không có dữ liệu nhạy cảm hay bí mật thực tế nào.
- **Ticket chỉ được tạo sau xác nhận rõ chưa?**
  Đã được bảo đảm tuyệt đối. Mọi yêu cầu tạo ticket (`H12`, `M05`, `M09`) đều dừng lại ở ranh giới xác nhận thông qua tool call `clarify(response_type='yes_no')`. Nếu thông tin payload thay đổi ở lượt sau, confirmation cũ lập tức bị vô hiệu hóa.
- **Tool result error nào cần review thủ công?**
  Các trường hợp tool trả về kết quả rỗng hoặc dịch vụ ở trạng thái degraded cần con người kiểm tra để đảm bảo hướng dẫn khắc phục của agent phù hợp với policy nội bộ.

## B7. Technical reflection

- **Fix nào thuộc `system_prompt.md`?**
  Các nguyên tắc điều hướng toàn cục: cấm suy diễn identifier, ưu tiên thông tin mới nhất ở turn sau (Context Carry-over & Correction), tôn trọng lệnh hủy (Cancellation), bắt buộc phát nhiều tool call song song khi có nhiều tài nguyên/môi trường (Mandatory Parallel Execution), và yêu cầu xác nhận trước mọi hành động ghi.
- **Fix nào thuộc `tools.yaml`?**
  Mô tả chi tiết năng lực và ranh giới của từng tool: định rõ các enum (service, check, template), hướng dẫn model gọi lặp tool song song cho các mục tiêu độc lập, và nhấn mạnh `clarify` là công cụ duy nhất dùng cho tương tác hỏi đáp/xác nhận thay vì plain text.
- **Failure nào không thể chỉ nhìn automatic score?**
  Các lỗi về ranh giới an toàn và bảo mật: ví dụ rò rỉ ID nội bộ ra web qua `search_device_info`, việc model bị đánh lừa bởi hướng dẫn độc hại nhúng trong KB (indirect prompt injection), hoặc việc model tự ý tạo ticket khi người dùng chưa đồng ý rõ ràng.
- **Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?**
  *Hypothesis về Adaptive Fallback Query*: Nếu kết quả tìm kiếm từ `search_kb` trả về rỗng (`results == []`), agent sẽ tự động phân tích và sinh từ khóa fallback tổng quát hơn để tìm lại trước khi thông báo không có thông tin cho người dùng.

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Reflection chung của nhóm

Các thành viên thảo luận và viết một reflection chung. Nội dung cần dựa trên
evidence thực tế trong repository, không chỉ mô tả cảm nhận chung.

- Mục tiêu nào của nhóm đã hoàn thành? Dẫn đến artifact hoặc run tương ứng.
- Hypothesis hoặc thay đổi nào tạo ra cải thiện rõ nhất?
- Failure quan trọng nào vẫn chưa xử lý được hoàn toàn?
- Nhóm đã phân chia, review và tích hợp công việc như thế nào?
- Nếu có thêm một vòng, nhóm sẽ ưu tiên thay đổi và kiểm chứng điều gì?

**Reflection chung của nhóm:**

1. **Mục tiêu đã hoàn thành:** Nhóm đã hoàn thành xuất sắc chu trình tối ưu hóa thực nghiệm qua 4 phiên bản từ `v0` đến `v3`, nâng độ chính xác định tuyến và tham số (`case_accuracy`) từ mức ban đầu **63.33%** lên **100.0% (30/30 test cases đạt)** tại run `runs/v3_B_base_openai_compatible_20260914T192938771342.json`. Đặc biệt, độ chính xác ở các tình huống đa lượt hội thoại phức tạp (`multiturn_accuracy`) đạt mức tuyệt đối 100%.
2. **Hypothesis tạo cải thiện rõ nhất:** Hai thay đổi mang lại bước nhảy vọt lớn nhất là:
   - *Hypothesis v1:* Loại bỏ định dạng JSON cưỡng bức trong prompt văn bản, cấm tự suy diễn identifier và bắt buộc gọi `clarify` khi thiếu thông tin giúp accuracy tăng vọt từ 63.33% lên 79.31%.
   - *Hypothesis v3:* Bổ sung quy định bắt buộc thực thi công cụ song song (*Mandatory Parallel Execution*) cho các yêu cầu so sánh môi trường/thiết bị và chẩn đoán đa nguồn, kết hợp khai thác mô hình hỗ trợ native parallel tool calling (`qwen/qwen3.8-27b`), giúp giải quyết triệt để 100% các ca khó còn lại (`H13`, `H15`, `H16`, `H17`, `H18`, `M08`).
3. **Giới hạn & Thách thức đã giải quyết:** Thách thức lớn nhất là model ban đầu có xu hướng chỉ gọi 1 tool duy nhất trong một turn. Nhóm đã giải quyết bằng cách tác động đồng thời ở cả hai tầng: bổ sung quy tắc gọi song song trong `system_prompt.md` và tinh chỉnh mô tả trong `tools.yaml` hướng dẫn rõ việc gọi lặp tool cho từng đối tượng mục tiêu.
4. **Phối hợp và tích hợp công việc:** Nhóm trưởng (Tạ Việt Cường) chủ trì kiến trúc prompt và thực nghiệm phiên bản; các thành viên phối hợp độc lập trên các nhánh riêng (`contrib/`) và tích hợp qua Pull Request vào nhánh `main` có đối soát kỹ thuật chặt chẽ.

## C2. Self-reflection của từng thành viên

Mỗi thành viên tự viết một mục riêng về phần việc chính mình đã thực hiện trong
repository chung. Không viết thay hoặc gộp nhiều thành viên vào một câu trả lời.
Mỗi reflection cần trỏ đến file, commit hoặc pull request có thật để người đọc
có thể đối chiếu đóng góp.

Sao chép mẫu dưới đây cho từng thành viên:

### Tạ Việt Cường — 02560

- **Vai trò/phần việc được nhận:** Prompt Architect / Team Lead
- **Những gì tôi đã thay đổi trong repo chung:** 
  - Thiết lập môi trường ảo `.venv` cô lập và cấu hình adapter cho đa provider (`openai_compatible` và `openrouter`).
  - Xây dựng, thực thi và điều phối chu trình 4 phiên bản thực nghiệm (`v0` $\rightarrow$ `v1` $\rightarrow$ `v2` $\rightarrow$ `v3`), đưa `case_accuracy` từ 63.33% lên 100% (30/30 passed) trên bộ `eval_base.json`.
  - Tối ưu hóa `artifacts/system_prompt.md`, `artifacts/tools.yaml`, quản lý `version_log.csv` và phân tích failure traces.
- **File hoặc artifact liên quan:** `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/`.
- **Commit hash hoặc pull request:** Commit `0293040` trên nhánh `cuongtv` ([Pull Request #1](https://github.com/ratrichero/K4-Day04-02560-TaVietCuong/pull/1)).
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Phát hiện việc starter prompt ép trả về JSON format khiến model OpenAI SDK cố gắng gọi tool ảo mang tên "JSON", dẫn tới lỗi BadRequestError 400. Tôi đã loại bỏ ràng buộc văn bản này khỏi prompt và chuyển toàn bộ việc truyền tham số sang cấu trúc function call chuẩn, kết hợp khai thác khả năng parallel tool calling của model `qwen/qwen3.8-27b` để giải quyết triệt để các bài toán so sánh nhiều môi trường và chẩn đoán đa nguồn.
- **Khó khăn tôi gặp và cách tôi xử lý:** Model ban đầu chỉ gọi 1 tool duy nhất ngay cả khi người dùng yêu cầu kiểm tra cả 2 môi trường hoặc cả thiết bị lẫn trạng thái dịch vụ. Tôi đã xử lý bằng cách cập nhật cả `system_prompt.md` (mục Mandatory Parallel Tool Execution) và `tools.yaml` (bổ sung hướng dẫn gọi lặp song song), giúp model phát đồng thời 2-3 tool calls trong cùng một turn với 100% độ chính xác tham số.
- **Điều tôi học được từ phần việc này:** Hiểu sâu sắc mối quan hệ cộng sinh giữa System Prompt, Tool Descriptions và Model Capabilities. Tối ưu agent không chỉ nằm ở việc sửa câu chữ prompt mà còn là tinh chỉnh interface schema và lựa chọn model có khả năng tool calling tương thích.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Tôi sẽ sớm xây dựng script tự động so sánh diff giữa các file JSON runs để trực quan hóa ngay lập tức các ca regression sau mỗi lần thay đổi prompt.

### Chung Văn Duy — 02854
*(Thành viên tự điền sau khi hoàn thành phần việc Tool & Schema Engineer)*

### Dương Đạt Khang — 02624
*(Thành viên tự điền sau khi hoàn thành phần việc Eval & Red-Team Specialist)*

### Trần Ngọc Chinh — 02720
*(Thành viên tự điền sau khi hoàn thành phần việc UI & Report Coordinator)*

Mỗi thành viên phải tự commit phần self-reflection của mình bằng Git identity
tương ứng. Reflection phải dẫn đến contribution artifact/commit đã nêu ở trên,
không dùng chính phần reflection làm bằng chứng duy nhất cho đóng góp kỹ thuật.

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAMMATES.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:
