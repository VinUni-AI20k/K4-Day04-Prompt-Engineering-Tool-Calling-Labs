# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team:
- Members:
- Provider/model: OpenAI / gpt-4o-mini

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Northstar Helpdesk Agent là trợ lý IT service desk dùng dữ liệu giả lập để hỗ trợ kiểm tra trạng thái dịch vụ, chẩn đoán thiết bị, tra cứu nhân viên, tìm hướng dẫn KB/chính sách, format incident report và tạo ticket sau khi có xác nhận rõ ràng. Agent chỉ xử lý các yêu cầu trong phạm vi IT helpdesk, không tự đoán asset ID/employee ID, không yêu cầu hoặc lưu secret, và không gửi dữ liệu nội bộ ra công cụ external search.

**Link dùng thử:**

> URL: Demo local: http://localhost:8501 sau khi chạy `streamlit run app.py` trong thư mục `starter_v0`.

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
| search_kb | Tìm hướng dẫn trong IT knowledge base local | core |
| check_service_status | Kiểm tra trạng thái dịch vụ dùng chung như VPN, email, SSO, Wi-Fi, printing | core |
| inspect_device | Đọc inventory và diagnostic snapshot của một asset cụ thể | core |
| lookup_user | Tra cứu directory record theo employee ID | core |
| format_incident_report | Format các findings đã có thành incident report | core |
| policy | Tìm trong chính sách IT nội bộ | optional built-in |
| create_ticket | Tạo ticket local sau khi có xác nhận rõ ràng | optional built-in |
| search_device_info | Tìm thông tin công khai về manufacturer/model trên web | optional built-in |

## A3. Câu hỏi mẫu

1. Dịch vụ VPN production hiện có đang gặp sự cố không?
2. Kiểm tra riêng kết nối VPN trên LT-204.
3. VPN trên LT-204 lỗi; kiểm tra cả trạng thái VPN production và máy đó.
4. Tạo ticket mức high cho lỗi VPN trên LT-204 giúp mình.
5. Kiểm tra Wi-Fi trên laptop của mình giúp nhé.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Kiểm tra trạng thái VPN production bằng Streamlit UI | check_service_status(service=vpn, environment=production) | Evidence UI baseline v0 | transcripts/ui_20260914T182119000929.transcript.json |
| Kiểm tra diagnostic VPN của LT-204 bằng CLI chat | inspect_device(asset_id=LT-204, check=vpn) | Evidence CLI baseline v0 | transcripts/v0_openai_20260914T182247374274.transcript.json |

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
| G01_missing_asset_id_clarify | Thiếu asset ID khi user báo lỗi laptop | Agent gọi clarify để hỏi asset ID, không tự đoán mã máy | Pending run |
| G02_dual_service_same_tool_diff_args | Một request cần kiểm tra hai service khác nhau | Agent gọi check_service_status hai lần cho vpn và sso production | Pending run |
| G03_ambiguous_intent_account | Intent/account information chưa đủ rõ | Agent hỏi lại hoặc route đúng theo yêu cầu account trong case | Pending run |
| G04_format_existing_findings_handoff | User đã cung cấp findings và chỉ yêu cầu format | Agent gọi format_incident_report, không inspect/fetch lại | Pending run |
| G05_search_device_info_specs_safe | Tìm thông tin public specs của thiết bị | Agent dùng search_device_info với manufacturer/model public, không gửi internal ID | Pending run |
| G06_multiturn_multiple_assets | Multi-turn với nhiều asset cần kiểm tra | Agent giữ context và gọi inspect_device cho các asset đúng | Pending run |
| G07_multiturn_environment_correction | User sửa environment ở lượt sau | Agent dùng environment mới nhất, không dùng thông tin cũ | Pending run |
| G08_multiturn_cancellation_flow | User hủy yêu cầu trước đó | Agent không gọi action/tool cũ sau khi user cancel | Pending run |
| G09_multiturn_stale_confirmation | Confirmation cũ mất hiệu lực khi payload đổi | Agent hỏi xác nhận lại, không tạo ticket ngay | Pending run |
| G10_multiturn_switch_employee_to_asset | User chuyển từ tra employee sang inspect asset | Agent làm theo intent mới nhất và gọi tool phù hợp | Pending run |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
| UI turn 1: Kiểm tra trạng thái VPN production | v0 | check_service_status(service=vpn, environment=production) | transcripts/ui_20260914T182119000929.transcript.json | Agent route đúng sang tool kiểm tra trạng thái dịch vụ dùng chung, trả về VPN degraded và dẫn incident INC-1042. |
| CLI chat: Kiểm tra VPN trên LT-204 | v0 | inspect_device(asset_id=LT-204, check=vpn) | transcripts/v0_openai_20260914T182247374274.transcript.json | Agent route đúng sang tool inspect thiết bị với asset LT-204 và phạm vi diagnostic là VPN. |

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
