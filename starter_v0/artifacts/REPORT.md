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

### Thành viên A (Prompt Architect) — [MSSV]

- **Vai trò/phần việc được nhận:** Quản lý system_prompt.md, format JSON, context carry-over & version hash.
- **Những gì tôi đã thay đổi trong repo chung:** [Điền thay đổi]
- **File hoặc artifact liên quan:** `artifacts/system_prompt.md`
- **Commit hash hoặc pull request:** [Điền hash]
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** [Điền quyết định]
- **Khó khăn tôi gặp và cách tôi xử lý:** [Điền khó khăn]
- **Điều tôi học được từ phần việc này:** [Điền bài học]
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** [Điền ý tưởng cải thiện]

### Thành viên B (Tool & Schema Engineer) — [MSSV]

- **Vai trò/phần việc được nhận:** Quản lý tools.yaml, chuẩn hóa enums/arguments, đồng bộ tool name.
- **Những gì tôi đã thay đổi trong repo chung:** [Điền thay đổi]
- **File hoặc artifact liên quan:** `artifacts/tools.yaml`
- **Commit hash hoặc pull request:** [Điền hash]
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** [Điền quyết định]
- **Khó khăn tôi gặp và cách tôi xử lý:** [Điền khó khăn]
- **Điều tôi học được từ phần việc này:** [Điền bài học]
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** [Điền ý tưởng cải thiện]

### Thành viên C (Eval & Red-Team) — [MSSV]

- **Vai trò/phần việc được nhận:** Tác giả 10 cases eval_group.json, kiểm thử 12 adversarial attacks.
- **Những gì tôi đã thay đổi trong repo chung:** [Điền thay đổi]
- **File hoặc artifact liên quan:** `data/eval_group.json`
- **Commit hash hoặc pull request:** [Điền hash]
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** [Điền quyết định]
- **Khó khăn tôi gặp và cách tôi xử lý:** [Điền khó khăn]
- **Điều tôi học được từ phần việc này:** [Điền bài học]
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** [Điền ý tưởng cải thiện]

### Thành viên D (UI & Report Coordinator) — [Điền MSSV của bạn]

- **Vai trò/phần việc được nhận:** Dựng Live Chat Streamlit, test kịch bản demo, tổng hợp REPORT.md.
- **Những gì tôi đã thay đổi trong repo chung:** Xây dựng giao diện Streamlit `app.py`, cấu hình thư viện UI, và thiết kế lại cấu trúc báo cáo.
- **File hoặc artifact liên quan:** `app.py`, `requirements.txt`, `artifacts/REPORT.md`
- **Commit hash hoặc pull request:** [Điền hash sau khi push code]
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tái sử dụng `run_model_tool_loop` từ `chat.py` kết hợp với `st.session_state` của Streamlit để giữ đúng flow gọi tool gốc của agent thay vì viết lại từ đầu. Sử dụng `st.expander` cho các tool events để giao diện nhìn gọn gàng nhưng vẫn kiểm chứng (audit) được tham số args.
- **Khó khăn tôi gặp và cách tôi xử lý:** Quản lý lịch sử hội thoại (history window) trong Streamlit để không bị đầy context. Xử lý bằng cách duy trì hai luồng list riêng biệt: `history` cho agent context và `display_messages` cho render giao diện.
- **Điều tôi học được từ phần việc này:** Hiểu rõ cách thức hoạt động của tool-loop backend (nhận request -> gọi models -> map functions -> lấy kết quả) và cách ghép nối nó vào một framework UI reactive.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** [Ghi ý kiến của bạn, ví dụ: Thêm nút tải/export lịch sử chat ra file Markdown]

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
