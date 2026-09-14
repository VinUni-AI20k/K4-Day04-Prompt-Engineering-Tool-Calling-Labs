# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team: 5AESIUNHAN
- Members:
> 1. Phạm Quang Huy - 2A202602900
> 2. Đỗ Thanh Tùng - 2A202602845
> 3. Trần Võ Hoàng Nguyên - 2A202602551
> 4. Ninh Quang Minh - 2A202602432
> 5. Nguyễn Như Tài - 2A202602976
- Provider/model: openai / gpt-4o-mini

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

### Họ tên — MSSV

- **Vai trò/phần việc được nhận:**
- **Những gì tôi đã thay đổi trong repo chung:**
- **File hoặc artifact liên quan:**
- **Commit hash hoặc pull request:**
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
- **Khó khăn tôi gặp và cách tôi xử lý:**
- **Điều tôi học được từ phần việc này:**
- **Nếu làm lại, tôi sẽ cải thiện điều gì:**

### Đỗ Thanh Tùng — 2A202602845

- **Vai trò/phần việc được nhận:** Test & Evaluation Designer (Thành viên 3) — thiết kế bộ eval riêng của nhóm và chạy suite `group`.

- **Những gì tôi đã thay đổi trong repo chung:** Viết 10 test case original vào `eval_group.json` (5 single-turn + 5 multi-turn), chạy baseline `v0` và commit run evidence. Ngoài ra tổng hợp 4 vùng hành vi mà bộ `base` không kiểm tra và gửi cho Thành viên 1 làm input cho prompt v1–v3.

- **File hoặc artifact liên quan:** `starter_v0/data/eval_group.json`; `starter_v0/runs/v0_B_group_openai_20260914T190322801149.json`

- **Commit hash hoặc pull request:** `093781d` (10 test cases), `69a4534` (v0 run evidence) — branch `contrib/tungne1311`

- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Trước khi chốt bộ đề, tôi đối chiếu từng expected answer với `company_policy/` và `helpdesk_data/`. Nhờ đó phát hiện một case tôi viết ban đầu hỏi về thời hạn phản hồi ticket mức `critical` — nội dung này không tồn tại trong corpus, và từ khóa `critical` lại nằm ở `incident-response-policy.md` chứ không phải `ticketing-policy.md`. Nếu giữ nguyên, case sẽ FAIL bất kể prompt tốt đến đâu, tức là đo nhiễu chứ không đo năng lực. Tôi viết lại thành câu hỏi về điều kiện bắt buộc trước khi tạo ticket, khớp đúng mục *Confirmation boundary*. Quyết định thứ hai: khi trao đổi với Thành viên 1 tôi chỉ gửi nguyên tắc hành vi, không gửi nội dung case hay expected tool call, để suite `group` giữ được giá trị kiểm chứng độc lập cho prompt v3.

- **Khó khăn tôi gặp và cách tôi xử lý:** Khó khăn lớn nhất là ban đầu tôi hiểu sai cơ chế chấm multi-turn. Tôi viết 5 case nhiều lượt như một cuộc chat thật, nhưng khi đọc kỹ `run_eval.py` mới thấy evaluator gộp toàn bộ các lượt thành một message duy nhất và chỉ chấm lượt cuối cùng. Tôi phải viết lại cả 5 case sao cho lượt cuối tự nó đủ thông tin để xác định tool call, còn các lượt trước chỉ đóng vai trò ngữ cảnh. Một khó khăn nhỏ hơn là thư mục `runs/` nằm trong `.gitignore`, nên `git add` bỏ qua file run mà không báo lỗi; tôi tưởng đã commit xong nhưng thực tế chưa, phải dùng `git add -f` mới đưa được run evidence vào lịch sử.

- **Điều tôi học được từ phần việc này:** Tôi học được rằng metric không thay thế được việc đọc `tool_results`. Case `GM07` trên bảng kết quả chỉ hiện đúng một dòng FAIL, nhưng khi mở tool result ra tôi mới thấy agent đã thực sự gọi `create_ticket` với `confirmed=false` — tức là lớp prompt đã thủng, và thứ chặn lại là tool implementation trả về `needs_confirmation`. Nếu chỉ nhìn con số 8/10 thì sẽ bỏ qua đúng chi tiết quan trọng nhất của run này. Tôi cũng học được rằng expected answer phải được đối chiếu với dữ liệu nguồn trước khi chốt, vì một case hỏi thứ không tồn tại trong corpus sẽ FAIL mãi mãi dù prompt có tốt đến đâu.

- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Baseline `v0` đã PASS 8/10, nghĩa là bộ đề của tôi chỉ có 2 case thực sự phân biệt được v0 với v3. Nếu làm lại, tôi sẽ chạy thử một lần trên baseline để calibrate độ khó trước khi chốt 10 case, thay vì phát hiện điều đó sau khi đã commit. Tôi cũng sẽ phân bổ case đều hơn giữa các tool — bộ đề hiện tập trung vào routing và confirmation boundary, còn `format_incident_report` thì chưa có case nào.

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
