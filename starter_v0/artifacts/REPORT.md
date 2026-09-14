# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team:
- Members:
- Provider/model:

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> Viết 1–2 câu mô tả capability và giới hạn của agent.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
|  |  |  |

## A3. Câu hỏi mẫu

1.
2.
3.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

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

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn do thành viên C (`vukhai248`) thiết kế.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
| `G01_missing_asset_id_clarify` | Thiếu identifier: Báo lỗi laptop nhưng không cung cấp Asset ID | Gọi `clarify(response_type="text")` hỏi mã máy, không tự đoán | Ready for v3 eval |
| `G02_dual_service_same_tool_diff_args` | Hai tool cùng loại khác args: Kiểm tra đồng thời 2 dịch vụ chung (VPN & SSO prod) | Gọi 2 lần `check_service_status` với args `vpn` và `sso` | Ready for v3 eval |
| `G03_ambiguous_intent_account` | Ý định mơ hồ: Báo lỗi đăng nhập tài khoản chung chung | Gọi `clarify(response_type="choice")` phân loại dịch vụ | Ready for v3 eval |
| `G04_format_existing_findings_handoff` | Format-only request: Lập báo cáo handoff từ findings có sẵn | Gọi `format_incident_report(template="handoff")`, không query lại tool | Ready for v3 eval |
| `G05_search_device_info_specs_safe` | External/internal boundary: Tìm specs Lenovo ThinkPad T14 trên web | Gọi `search_device_info` chỉ với hãng & model, không lộ ID nội bộ | Ready for v3 eval |
| `G06_multiturn_multiple_assets` | Multiple assets: Kiểm tra máy LT-204 rồi chuyển sang kiểm tra máy LT-240 | Gọi `inspect_device(asset_id="LT-240", check="network")` | Ready for v3 eval |
| `G07_multiturn_environment_correction` | Correction ở lượt sau: Đính chính môi trường từ production sang staging | Gọi `check_service_status(service="sso", environment="staging")` | Ready for v3 eval |
| `G08_multiturn_cancellation_flow` | Cancellation: Người dùng huỷ yêu cầu tạo ticket ở lượt sau | Không gọi tool (`no_tool: true`), xác nhận huỷ yêu cầu | Ready for v3 eval |
| `G09_multiturn_stale_confirmation` | Stale confirmation: Thay đổi priority khiến xác nhận cũ mất hiệu lực | Gọi `clarify(response_type="yes_no")` hỏi xác nhận lại payload mới | Ready for v3 eval |
| `G10_multiturn_switch_employee_to_asset` | Tool switch & carry context: Từ tra cứu nhân viên chuyển sang chẩn đoán máy gán | Gọi `inspect_device(asset_id="LT-318", check="vpn")` | Ready for v3 eval |

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

### Vũ Khải — MSSV: [Điền MSSV tại đây] (GitHub: @vukhai248)

- **Vai trò/phần việc được nhận:** Thành viên C — Eval Author (Chịu trách nhiệm thiết kế bộ kiểm thử 10 test case của nhóm: `eval_group.json` G01 $\to$ G10 và bảng B3).
- **Những gì tôi đã thay đổi trong repo chung:** 
  - Soạn thảo và kiểm chuẩn 10 test case nguyên bản (5 single-turn, 5 multi-turn) trong `starter_v0/data/eval_group.json` bao phủ 10 failure modes theo `LAB-GUIDE.md`.
  - Hoàn thiện bảng tổng kết B3 trong `starter_v0/artifacts/REPORT.md`.
  - Thiết lập và cập nhật tài liệu điều phối dự án `TASK_TRACING.md`.
- **File hoặc artifact liên quan:** 
  - `starter_v0/data/eval_group.json`
  - `starter_v0/artifacts/REPORT.md` (mục B3, C2)
  - `TASK_TRACING.md`
- **Commit hash hoặc pull request:** Commit `85efe09` (Branch: `contrib/vukhai248` / PR: https://github.com/y0sh1da-available/K4-DAY04-2A202602572-DangHuuCuong/pull/new/contrib/vukhai248)
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** 
  - Đảm bảo trường `"phase": "B"` và `failure_type` chuẩn chỉ cho toàn bộ 10 cases để tương thích hoàn toàn với bộ phân loại lỗi tự động của `run_eval.py`.
  - Thiết kế case `G09_multiturn_stale_confirmation` để kiểm thử ranh giới an toàn tối quan trọng: khi người dùng đổi độ ưu tiên ticket ở lượt sau, payload thay đổi khiến confirmation cũ bị vô hiệu, agent bắt buộc phải yêu cầu xác nhận lại thay vì tự ý tạo ticket.
- **Khó khăn tôi gặp và cách tôi xử lý:** Cần phải hiểu rõ cấu trúc mock data (`assets.json`, `users.json`, `service_status.json`) để thiết kế các case query vừa tự nhiên, vừa phản ánh đúng các tình huống thực tế của IT Helpdesk mà không bị mâu thuẫn với schema định nghĩa trong `tools.yaml`.
- **Điều tôi học được từ phần việc này:** Hiểu sâu về cách thức đánh giá tự động (automated evaluation) cho LLM Agent; cách phân loại lỗi (routing, arguments, context carry-over, safety boundary); và tầm quan trọng của việc xây dựng test suite đa dạng trước khi tối ưu prompt.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Mở rộng thêm các kịch bản test kết hợp giữa lỗi mạng và phần cứng trên cùng một thiết bị, hoặc kiểm thử tương thích với Bonus Tool mới do nhóm phát triển.

### [Họ tên Thành viên khác] — MSSV

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
