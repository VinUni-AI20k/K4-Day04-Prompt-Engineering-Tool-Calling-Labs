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

### Ngô Gia Quốc — 2A202602757

- **Vai trò/phần việc được nhận:** Phụ trách Tool Declarations: audit capability, tên tool, description, schema và argument convention của các tool; đối chiếu declaration với `TOOL.md`, implementation, registry và eval; cải thiện `tools.yaml` theo evidence từ baseline.
- **Những gì tôi đã thay đổi trong repo chung:** Tôi cập nhật model-facing descriptions trong `tools.yaml` mà không đổi tên tool, registry, enum, required fields, implementation hoặc fixed eval. Ở v1, tôi làm rõ ranh giới giữa status service/device/KB, yêu cầu identifier rõ ràng, mapping diagnostic domain sang `inspect_device.check`, boundary của lookup user, formatter-only, write confirmation và external-data boundary. Thay đổi này cải thiện base eval từ 21/30 lên 27/30 cases pass. Sau khi phân tích v1, tôi thực hiện patch v2 để phân biệt `search_kb.category=email` cho Outlook/profile với `account` cho login/MFA/account lock, đồng thời nhấn mạnh confirmation của payload ticket đầy đủ phải dùng `clarify(response_type=yes_no)` thay vì `text`.
- **File hoặc artifact liên quan:** `artifacts/tools.yaml`; evidence baseline `runs/v0_B_base_openai_20260914T182709526456.json`; evidence v1 `runs/v1_B_base_openai_20260914T185746682098.json`; ghi chú audit/handoff `../../agent.md`.
- **Commit hash hoặc pull request:** Chưa có tại thời điểm viết report. Tôi cần tự tạo commit bằng Git identity của mình sau khi chốt và verify v2; commit đó sẽ được cập nhật vào đây.
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tôi giữ nguyên tên tool, enum, required fields, registry và fixed eval; chỉ cải thiện tool declaration theo từng hypothesis nhỏ. Lý do là tool name/schema là một phần interface model và evaluator dùng để đối chiếu, nên đổi đồng thời nhiều thành phần sẽ khó truy nguyên nguyên nhân metric thay đổi và có thể gây regression. Tôi cũng không sửa implementation vì smoke tests xác nhận validation của tool hoạt động đúng; failure ban đầu chủ yếu do model chọn tool/argument/boundary sai.
- **Khó khăn tôi gặp và cách tôi xử lý:** Ban đầu smoke test báo `ModuleNotFoundError: No module named 'yaml'` vì terminal chưa dùng environment đã cài PyYAML. Tôi kích hoạt đúng `.venv` và xác nhận lại bằng các smoke tests. Khi đọc v1, tôi phát hiện một regression H03 (`Outlook profile` bị route sang category `account`), H12 đã an toàn hơn nhưng dùng `clarify(text)` thay vì `yes_no`, và H19 vẫn tự suy diễn environment demo/QA. Tôi xử lý H03/H12 ở declaration và bàn giao H19 cho phần system prompt vì đây là rule enum ambiguity toàn cục.
- **Điều tôi học được từ phần việc này:** Tool name, description và JSON schema đều là một phần của prompt. Implementation chạy đúng không đảm bảo model chọn đúng tool. Evidence theo từng case và trace/tool result quan trọng hơn metric tổng; ví dụ v1 vừa cho thấy 7 lỗi baseline được cải thiện, vừa phát hiện H03 regression và H19 là vấn đề cần xử lý ở system prompt.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Tôi sẽ chuẩn bị mapping capability-to-tool và deterministic declaration/registry validation ngay từ đầu, chạy một nhóm smoke security checks sớm hơn, rồi tách experiment rõ hơn: một version chỉ sửa declaration, version kế tiếp chỉ sửa system prompt. Tôi cũng sẽ chạy extension/adversarial ngay sau khi prompt global được tích hợp để xác minh ticket confirmation, injection boundary và external-data boundary cùng nhau.

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
