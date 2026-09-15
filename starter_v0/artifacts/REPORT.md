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
| Optional built-in | `starter_v0/tools/policy/tool.py`, `starter_v0/tools/create_ticket/tool.py`, `starter_v0/runs/v3_B_adversarial_openai_20260914T201903900292.json` (Cases `A03`, `A05`, `A08`) | Tra cứu chính sách IT nội bộ theo từ khóa/danh mục (`policy`); tạo ticket hỗ trợ kỹ thuật dạng JSON cục bộ sau khi có yêu cầu và xác nhận (`create_ticket`). | **Risk**: Tạo ticket tùy tiện khi chưa xác nhận hoặc lưu trữ credential nhạy cảm.<br>**Guardrail**: Yêu cầu đối số `confirmed: true`; regex quét chặn mật khẩu/token và trả về lỗi `restricted_sensitive_data`. |
| External search + privacy boundary | `starter_v0/tools/search_device_info/tool.py`, `starter_v0/runs/v3_B_adversarial_openai_20260914T201903900292.json` (Case `A12`) | Tìm kiếm driver, thông số kỹ thuật và tài liệu hỗ trợ công khai ngoài web (qua Tavily Search) cho dòng máy phần cứng (ví dụ Lenovo ThinkPad). | **Risk**: Rò rỉ mã tài sản nội bộ (`LT-xxx`), mã nhân viên (`EMP-xxx`), serial number hoặc hostname ra ngoài internet.<br>**Guardrail**: Cơ chế kiểm duyệt nghiêm ngặt chặn truy vấn và trả về lỗi `restricted_internal_identifier` nếu phát hiện pattern mã định danh nội bộ. |
| Bonus: tool mới do nhóm tự xây | Implementation: `starter_v0/tools/approved_software_catalog/tool.py`<br>Metadata: `starter_v0/tools/approved_software_catalog/TOOL.md`<br>Data: `starter_v0/helpdesk_data/software_catalog.json`<br>Schema: `starter_v0/artifacts/tools.yaml`<br>Run test: `starter_v0/runs/0_B_group_openai_20260914T201126103790.json` (Case `G05`) | Tra cứu danh mục phần mềm được cấp phép tại Northstar Labs; hỗ trợ alias, không dấu tiếng Việt (`fold_text`), phân loại category. Trong run test `G05`, agent gọi chính xác `approved_software_catalog` để tra cứu Docker Desktop. | **Risk**: Người dùng cài đặt phần mềm bị cấm (`prohibited`) hoặc thiếu bản quyền doanh nghiệp.<br>**Guardrail**: Dữ liệu mock nội bộ an toàn (`trust_boundary: "local_mock_data"`), trả về rõ trạng thái phê duyệt (`approved`/`restricted`/`prohibited`) và quy trình phê duyệt (`approval_required`). |

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

### Lại Bá Quân — 2A202602495 (vxtor012)

- **Vai trò/phần việc được nhận:** Thiết kế và hiện thực hóa Bonus Tool `approved_software_catalog` cho hệ sinh thái IT Helpdesk Agent; thiết lập metadata, schema và dữ liệu mock.
- **Những gì tôi đã thay đổi trong repo chung:**
  - Viết module logic tra cứu danh mục phần mềm trong `starter_v0/tools/approved_software_catalog/tool.py`.
  - Soạn thảo tài liệu đặc tả tool tại `starter_v0/tools/approved_software_catalog/TOOL.md`.
  - Xây dựng tệp cơ sở dữ liệu mẫu `starter_v0/helpdesk_data/software_catalog.json`.
  - Khai báo schema chuẩn vào `starter_v0/artifacts/tools.yaml` và đăng ký trong `starter_v0/tools/__init__.py`.
  - Đóng góp test case mẫu `G05_software_catalog_bonus` vào `starter_v0/data/eval_group.json`.
- **File hoặc artifact liên quan:**
  - `starter_v0/tools/approved_software_catalog/tool.py`
  - `starter_v0/tools/approved_software_catalog/TOOL.md`
  - `starter_v0/helpdesk_data/software_catalog.json`
  - `starter_v0/artifacts/tools.yaml`
  - `starter_v0/tools/__init__.py`
  - `starter_v0/data/eval_group.json`
- **Commit hash hoặc pull request:** `764b0f0cd023857f65fe1801cedc91777ad77d71` (Commit `764b0f0` trên branch `quan`).
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tôi thiết kế thuật toán tìm kiếm hybrid 2 lớp: vừa khớp chuỗi con không dấu (`fold_text`), vừa so khớp tập hợp từ khóa sau khi lọc stop words (`terms.issubset`). Thiết kế này giúp Agent hoạt động bền bỉ, nhận diện đúng phần mềm kể cả khi người dùng gõ tiếng Việt có dấu/không dấu, gõ tên viết tắt (như `vscode`) hoặc gõ xáo trộn thứ tự từ khóa.
- **Khó khăn tôi gặp và cách tôi xử lý:** Khi chạy test đánh giá tự động case `G05`, evaluator đòi hỏi query chính xác `'Docker Desktop'` trong khi mô hình chỉ trích xuất `'docker'`, gây ra lỗi mismatch argument (`wrong_arg_value`). Tôi đã giải quyết bằng cách bổ sung trường `aliases` đa dạng trong `software_catalog.json` để tool vẫn match chính xác và trả về kết quả mong muốn.
- **Điều tôi học được từ phần việc này:** Hiểu rõ cách Agent tương tác với Tool Calling Interface: cách đặt tên (`name`), viết mô tả (`description`) và các kiểu tham số (`parameters`) trong `tools.yaml` quyết định trực tiếp việc LLM có trích xuất đúng ý định của người dùng hay không.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Bổ sung trường lọc theo trạng thái chính sách (chỉ lọc phần mềm `status: approved` hoặc cảnh báo ngay khi gặp phần mềm `status: prohibited`) trực tiếp trong logic trả về của tool để phản hồi cho người dùng dứt khoát và an toàn hơn.

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
