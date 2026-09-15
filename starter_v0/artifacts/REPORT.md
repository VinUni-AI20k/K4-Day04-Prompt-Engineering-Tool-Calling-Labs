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

### Trần Thế Anh - 2A202602516

- **Vai trò/phần việc được nhận:** Tôi phụ trách vai trò C — Eval Author, thiết kế bộ G01–G10, chạy các suite đánh giá, kiểm tra tính hợp lệ của run, phân tích failure và tổng hợp evidence phục vụ report.
- **Những gì tôi đã thay đổi trong repo chung:** Tôi xây dựng đúng 10 case nguyên bản gồm 5 single-turn và 5 multi-turn; chuẩn hóa coverage cho routing, missing information, format-only, privacy boundary, correction, cancellation, confirmation và multiple-tool calls. Tôi cũng chạy group eval `v3`, tái xuất bảng phân tích và ghi lại kết quả review thủ công thay vì chỉ dựa vào nhãn PASS/FAIL.
- **File hoặc artifact liên quan:** `starter_v0/data/eval_group.json`, `starter_v0/artifacts/EVAL-EVIDENCE.md`, `starter_v0/artifacts/V0-FAILURE-ANALYSIS.md`, `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/run-analysis.csv` và `starter_v0/runs/v3_B_group_openrouter_20260914T233516261660.json`.
- **Commit hash hoặc pull request:** Commit kỹ thuật ban đầu `3371bdc` (`feat(eval): add group cases and baseline evidence`) và commit hoàn thiện `04f2f4f` (`feat(eval): finalize G01-G10 and group evidence`) trên branch `contrib/Thees-Anh-eval-final`, đã được gửi qua pull request vào repository chung.
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tôi thiết kế mỗi case tập trung vào một quyết định hành vi chính và dùng expected arguments ở mức đủ để grader kiểm tra chính xác. Với G01 và G08, tôi cố ý yêu cầu nhiều tool call có arguments khác nhau để phát hiện việc model bỏ sót, gộp hoặc tráo dữ liệu. Cách này giúp kết quả phản ánh khả năng giữ đúng context, thay vì chỉ kiểm tra model có gọi đúng tên tool hay không.
- **Khó khăn tôi gặp và cách tôi xử lý:** Khó khăn lớn nhất là phân biệt lỗi hành vi của agent với lỗi provider hoặc tool runtime. Tôi chỉ công nhận run khi `provider_error_cases == 0` và `measured_cases == total_cases`, sau đó đọc actual calls, arguments và tool results. Nhờ vậy tôi xác định G02 fail vì model tự ánh xạ “sandbox” thành `staging`, trong khi G05 được grader chấm PASS về routing/privacy nhưng external tool vẫn trả `missing_api_key`; hai kết quả này cần được diễn giải khác nhau.
- **Điều tôi học được từ phần việc này:** Tôi hiểu rằng accuracy tổng không đủ để kết luận agent hoạt động tốt. Eval cần có dataset cân bằng, metadata rõ, artifact hash để truy vết và review thủ công các trace. Tôi cũng thấy regression là tín hiệu quan trọng: chuỗi base thay đổi từ `0.7000` lên `0.8667`, giảm còn `0.8333`, rồi tăng lên `0.9667`, cho thấy mỗi thay đổi prompt/schema đều cần chạy lại cùng suite trước khi kết luận.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Tôi sẽ thống nhất provider/model và quy ước version với nhóm ngay từ đầu, chốt ma trận G01–G10 trước khi chạy để tránh tạo evidence trên dataset trung gian, đồng thời preflight cả OpenRouter và Tavily sớm hơn. Tôi cũng sẽ bổ sung một vòng regression cho G02 sau khi A/B cải thiện quy tắc xử lý environment mơ hồ và chỉ chạy extension khi external tool đã có key hợp lệ.

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
