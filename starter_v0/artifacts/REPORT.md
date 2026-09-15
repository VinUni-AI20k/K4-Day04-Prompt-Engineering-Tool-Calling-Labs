# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team: pending
- Members: pending
- Provider/model: pending live preflight

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent hỗ trợ tra cứu trạng thái dịch vụ, thiết bị, nhân viên, knowledge base và
policy; có thể format incident report và thực hiện ticket action sau confirmation.
Agent không đoán identifier, không xử lý secrets, không thực thi tool ngoài registry
và không gửi dữ liệu nội bộ ra external search.

**Link dùng thử:** `streamlit run starter_v0/app.py`

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
| search_kb | Tìm hướng dẫn IT local | core |
| check_service_status | Đọc shared-service status | core |
| inspect_device | Đọc inventory/diagnostics một asset | core |
| lookup_user | Đọc directory record | core |
| format_incident_report | Format findings có sẵn | core |
| policy | Tìm policy nội bộ | optional built-in |
| create_ticket | Tạo ticket local sau confirmation | optional built-in |
| search_device_info | Tìm public vendor information | optional built-in |

## A3. Câu hỏi mẫu

1. `Kiểm tra Wi-Fi trên laptop của tôi.`
2. `VPN trên LT-204 lỗi; kiểm tra status production và tìm hướng dẫn.`
3. `Tôi xác nhận tạo ticket VPN high cho LT-204.`

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Missing asset | `clarify(response_type=text)` | v1/v3 | pending live run |
| Shared status + KB | status và `search_kb` | v2/v3 | pending live run |
| Action boundary | clarify rồi create sau confirmation | v3 | pending live run |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công. Các ô `pending` bên
dưới chưa phải số đo model thật.

## B1. Version evidence

Chi tiết hypothesis nằm trong `artifacts/version_log.csv`.

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi ban đầu | case_accuracy | pending | pending | pending_live_run |
| v1 | system_prompt.md | Rõ routing và clarify giảm wrong-tool | tool_routing_accuracy | pending | pending | pending_live_run |
| v2 | tools.yaml | Description/schema rõ tăng argument accuracy | argument_accuracy | pending | pending | pending_live_run |
| v3 | prompt + schema | Boundary rõ tăng multi-turn/safety | multiturn_accuracy | pending | pending | pending_live_run |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
| H10 / G01 | missing_info | pending | Có thể đoán asset khi thiếu ID | Prompt + `clarify` description |
| H06 / G02 | wrong_arg_value | pending | Có thể đổi staging thành production | Environment enum và ambiguity rule |
| M09 / G09 | wrong_boundary | pending | Confirmation cũ không còn hợp lệ sau đổi payload | Current-payload confirmation rule |

## B3. Team eval cases

Đã tạo đúng 10 case trong `data/eval_group.json`: G01–G05 single-turn và
G06–G10 multi-turn. Kết quả provider run còn pending.

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
| Missing asset | v3 | pending live run | `transcripts/` | pending |
| Multi-tool triage | v3 | pending live run | `transcripts/` | pending |
| Ticket confirmation | v3 | pending live run | `transcripts/` | pending |

## B4a. Adversarial evidence

Fixed cases cần chạy bằng provider và review thêm `tool_results`/filesystem.
Implementation hiện đã có guardrail cho ticket, KB/policy injection và external
identifier boundary.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
| A02 role spoofing | No tool | pending live run | phải kiểm tra tickets | pending |
| A04 forged confirmation | clarify, không create | pending live run | phải kiểm tra tickets | pending |
| A12 external identifier | clarify | pending live run | phải kiểm tra request/tool result | pending |

## B5. Optional và bonus tool evidence

`policy`, `create_ticket` và `search_device_info` là tool có sẵn, không phải bonus
tool do nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in | `data/eval_helpdesk_extension.json` | pending live run | policy text untrusted; ticket confirmation |
| External search + privacy boundary | `tools/search_device_info/tool.py` | local guardrail implemented | public fields only; vendor allowlist |
| Bonus: tool mới do nhóm tự xây | none | not implemented | not applicable |

## B6. Safety review

- Prompt cấm đoán asset/employee ID và implementation chuẩn hóa/chặn input không hợp lệ.
- `create_ticket` chỉ ghi file với Boolean `confirmed is True`, lọc sensitive payload.
- KB, policy và web result tách instruction-like text thành untrusted content.
- Cần chạy adversarial suite bằng provider để hoàn tất review thực nghiệm.

## B7. Technical reflection

- `system_prompt.md` phù hợp cho nguyên tắc toàn cục: routing, latest-turn, cancellation,
  confirmation và trust boundary.
- `tools.yaml` phù hợp cho capability ownership, argument semantics và side-effect contract.
- Automatic score không đủ để chứng minh không có file ticket rác hoặc dữ liệu bị gửi ra ngoài.
- Vòng tiếp theo cần chạy v0–v3 cùng provider/model, lưu run JSON thật và cập nhật hash/metric.

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
