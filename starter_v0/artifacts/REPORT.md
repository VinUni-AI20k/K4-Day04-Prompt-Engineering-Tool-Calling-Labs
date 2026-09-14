# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team: K4-DAY04-2A202602531
- Members:
  - Đỗ Ngọc Phi (MSSV: 2A202602531) — A (Lead / Prompt Architect)
  - Phạm Cường Quốc (MSSV: 2A202602469) — B (Tool & Schema Engineer)
  - Đỗ Đức Đại (MSSV: 2A202602725) — C (Eval & Red-Team)
  - Nguyễn Trường Bảo (MSSV: 2A202602540) — D (UI & Report Coordinator)
- Provider/model: OpenAI / gpt-4o-mini (hỗ trợ OpenRouter, Gemini, Anthropic)

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

IT Helpdesk Agent hỗ trợ tự động hóa các tác vụ dịch vụ IT nội bộ: kiểm tra trạng thái dịch vụ chia sẻ (VPN, Email, SSO...), tra cứu cấu hình và chẩn đoán thiết bị, tra cứu nhân viên, tìm kiếm hướng dẫn trong Knowledge Base, tra cứu chính sách IT và tạo ticket hỗ trợ khi có xác nhận. Giới hạn: Agent tuyệt đối không tự đoán định danh (asset ID/employee ID), không yêu cầu thông tin nhạy cảm (mật khẩu, OTP) và không tự ý tạo ticket khi chưa có xác nhận từ người dùng.

**Link dùng thử:**

> URL: `http://localhost:8501` (Chạy bằng lệnh `streamlit run app.py` tại thư mục `starter_v0`)

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung thông tin hoặc xin xác nhận trước khi hành động | core |
| search_kb | Tìm kiếm bài viết hướng dẫn trong Knowledge Base nội bộ | core |
| check_service_status | Đọc trạng thái hoạt động của dịch vụ hệ thống (VPN, SSO, WiFi...) | core |
| inspect_device | Đọc thông tin cấu hình, bảo hành và chẩn đoán phần cứng thiết bị | core |
| lookup_user | Tra cứu thông tin danh bạ nhân viên và thiết bị được cấp theo ID | core |
| format_incident_report | Định dạng các phát hiện thành báo cáo sự cố chuẩn | core |
| policy | Tra cứu quy định, chính sách bảo mật và hỗ trợ IT nội bộ | optional / advanced |
| create_ticket | Tạo ticket hỗ trợ trong hệ thống sau khi có xác nhận rõ ràng | optional / advanced |
| search_device_info | Tra cứu thông số, driver thiết bị công khai qua Tavily Search API | optional / advanced |

## A3. Câu hỏi mẫu

1. "Kiểm tra trạng thái dịch vụ VPN production giúp mình."
2. "Tra cứu thông tin cấu hình và chẩn đoán của laptop mã LP-101."
3. "Tạo ticket yêu cầu thay bàn phím cho laptop LP-202 (đã xác nhận)."

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| 1. Tra cứu trạng thái dịch vụ VPN | `check_service_status(service_name="vpn")` | v0 (baseline hoạt động tốt) | `transcripts/v0_openai_demo_vpn.transcript.json` |
| 2. Người dùng báo hỏng máy nhưng thiếu mã | `clarify(question=..., category="text")` | v0/v1 (hỏi lại, không đoán mã máy) | `transcripts/v0_openai_demo_clarify.transcript.json` |
| 3. Người dùng sửa mã thiết bị ở lượt sau | `inspect_device(asset_id="LP-202")` (sau khi đính chính) | v1 (xử lý ngữ cảnh multi-turn) | `transcripts/v1_openai_demo_multiturn.transcript.json` |
| 4. Yêu cầu tạo ticket cần xin xác nhận | `clarify` (xin confirm) $\rightarrow$ `create_ticket(confirmed=True)` | v2/v3 (bảo đảm an toàn action boundary) | `transcripts/v2_openai_demo_ticket.transcript.json` |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

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

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

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

> Viết reflection tại đây và dẫn link/path đến evidence liên quan.

## C2. Self-reflection của từng thành viên

Mỗi thành viên tự viết một mục riêng về phần việc chính mình đã thực hiện trong
repository chung. Không viết thay hoặc gộp nhiều thành viên vào một câu trả lời.
Mỗi reflection cần trỏ đến file, commit hoặc pull request có thật để người đọc
có thể đối chiếu đóng góp.

Sao chép mẫu dưới đây cho từng thành viên:

### Nguyễn Trường Bảo — 2A202602540

- **Vai trò/phần việc được nhận:** D — UI & Report Coordinator
- **Những gì tôi đã thay đổi trong repo chung:** Xây dựng giao diện Streamlit Live Chat (`starter_v0/app.py`), cập nhật thư viện vào `requirements.txt`, thiết lập và diễn tập 4 kịch bản demo (happy path, missing info clarify, multi-turn correction, action boundary confirmation), điều phối và tổng hợp bản báo cáo `REPORT.md`.
- **File hoặc artifact liên quan:** `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/artifacts/REPORT.md`
- **Commit hash hoặc pull request:** Branch `zewolkt3939` PR vào `main`
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tái sử dụng trực tiếp hàm `run_model_tool_loop` từ `chat.py` trong Streamlit UI thay vì viết lại agent loop mới; quyết định này bảo đảm 100% tính đồng nhất về logic gọi tool, số vòng lặp tối đa và định dạng ghi log transcript giữa giao diện tương tác và bộ chấm điểm đánh giá tự động (eval).
- **Khó khăn tôi gặp và cách tôi xử lý:** Xử lý hiển thị trực quan các vòng lặp tool calling đa lượt (multi-turn) và các lần gọi tool trung gian kèm trạng thái chờ phản hồi (`waiting_for_user`) trên Streamlit session_state; tôi giải quyết bằng cách bóc tách từng round trong `turn_record`, sử dụng `st.expander` để hiển thị tên tool, arguments và kết quả JSON trực quan, đồng thời lưu trữ đầy đủ transcript cho phiên chat.
- **Điều tôi học được từ phần việc này:** Hiểu sâu về luồng tương tác function calling của các mô hình LLM hiện đại, cách thiết kế giao diện có khả năng quan sát (observability) để kiểm chứng ranh giới an toàn và nhận biết sớm các lỗi chọn sai tool/arguments.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Xây dựng thêm tính năng replay lại các file transcript đã lưu từ trước trực tiếp trên giao diện để hỗ trợ Red-Team phân tích các ca thất bại nhanh hơn.

### Họ tên — MSSV

- **Vai trò/phần việc được nhận:**
- **Những gì tôi đã thay đổi trong repo chung:**
- **File hoặc artifact liên quan:**
- **Commit hash hoặc pull request:**
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
- **Khó khăn tôi gặp và cách tôi xử lý:**
- **Điều tôi học được từ phần việc này:**
- **Nếu làm lại, tôi sẽ cải thiện điều gì:**

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
