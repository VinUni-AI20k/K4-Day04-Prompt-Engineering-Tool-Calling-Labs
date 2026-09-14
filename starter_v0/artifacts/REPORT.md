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

### Lương Quang Huy — 2A202602982

- **Vai trò/phần việc được nhận:** B (Tool & Schema Engineer) — Quản lý `tools.yaml`, chuẩn hóa enums/arguments, đồng bộ tool name, cấu hình và bảo vệ ranh giới Tavily Search API.
- **Những gì tôi đã thay đổi trong repo chung:**
  - Tái cấu trúc và tối ưu hóa toàn bộ file `artifacts/tools.yaml` qua các phiên bản v1, v2, v3.
  - Phân định ranh giới rõ ràng giữa dịch vụ dùng chung toàn công ty (`check_service_status`) và thiết bị cá nhân (`inspect_device`).
  - Thiết lập điều kiện kích hoạt `clarify` khi thiếu định danh (`asset_id`, `employee_id`) hoặc môi trường mơ hồ.
  - Khóa chặt ranh giới action tool: ngăn chặn việc gọi thừa `create_ticket(confirmed=False)` khi chưa có sự xác nhận của người dùng.
  - Chuẩn hóa enums cho `search_kb` (`category`) và chính sách IT `policy` (`policy_area`).
  - Thiết lập ranh giới an toàn cho Tavily Search API (`search_device_info`), ngăn chặn việc rò rỉ mã nội bộ (LT-xxx, EMP-xxx) ra web.
  - Ghi nhận nhật ký các mốc thực nghiệm vào `artifacts/version_log.csv`.
- **File hoặc artifact liên quan:**
  - `starter_v0/artifacts/tools.yaml`
  - `starter_v0/artifacts/version_log.csv`
  - Các file run evidence: `runs/v0_B_base_openrouter_20260914T183347208745.json`, `runs/v1_B_base_openrouter_20260914T183603989734.json`, `runs/v2_B_base_openrouter_20260914T183916968133.json`, `runs/v3_B_base_openrouter_20260914T184022079006.json`, `runs/v3_B_extension_openrouter_20260914T184424771485.json`, `runs/v3_B_adversarial_openrouter_20260914T184555321591.json`.
- **Commit hash hoặc pull request:** Branch `B-LuongQuangHuy` (các commit tối ưu `tools.yaml` và `version_log.csv`).
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Ràng buộc chặt chẽ description của `create_ticket` để cấm gọi tool kể cả khi `confirmed=False` trong giai đoạn xin xác nhận. Điều này giúp loại bỏ hoàn toàn lỗi thừa tool (`extra_tool_call`), nâng độ chính xác của các ca xác nhận nhiều lượt (multi-turn) lên 100%.
- **Khó khăn tôi gặp và cách tôi xử lý:** Ban đầu gặp lỗi rate limit (429) do quota thấp khi chạy dồn dập nhiều requests trên Gemini Free Tier; tôi đã giải quyết bằng cách chuyển đổi provider sang OpenRouter (`openai/gpt-4o-mini`), giúp quá trình eval chạy ổn định 100% và đạt `provider_error_cases == 0`.
- **Điều tôi học được từ phần việc này:** Hiểu sâu sắc rằng Tool Description và JSON Schema đóng vai trò là một phần quan trọng của Prompt đối với LLM. Một schema được định nghĩa chặt chẽ với enums rõ ràng và mô tả ranh giới sắc nét có thể giải quyết dứt điểm các bài toán định tuyến phức tạp mà không cần phải viết prompt quá dài dòng.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Tôi sẽ xây dựng thêm một tool bonus mới (ví dụ: tra cứu kho phần mềm được cấp phép `approved_software_catalog`) với đầy đủ schema và ranh giới bảo mật để nhóm nhận thêm điểm bonus.

### Họ tên — MSSV (Dành cho thành viên tiếp theo)

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