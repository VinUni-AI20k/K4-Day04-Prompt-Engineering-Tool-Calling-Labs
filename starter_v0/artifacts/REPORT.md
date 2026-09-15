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

**Nguyễn Minh Đức - Vai trò B (Tool & Schema Engineer)**

Trong dự án này, tôi chịu trách nhiệm chính ở vai trò B, tập trung vào việc chuẩn hóa, bảo mật và đồng bộ hóa hệ thống công cụ (Tools) cho Agent. Dưới đây là các hạng mục công việc cốt lõi tôi đã thực hiện:

*   **Chuẩn hóa và đồng bộ Schema (Source of Truth):**
    Tôi đã tiến hành rà soát toàn bộ logic Python trong thư mục `tools/` (bao gồm `clarify.py`, `inspect_device.py`...) và chuyển đổi các cấu hình JSON Schema sang định dạng YAML. Mục tiêu là biến file `tools.yaml` thành cấu hình gốc duy nhất (source of truth) cho Agent, giải quyết triệt để tình trạng lệch pha giữa khai báo tham số và logic code.
    *   *Evidence:* Xem file [tools.yaml](./tools.yaml) đã được cập nhật chuẩn xác.

Sao chép mẫu dưới đây cho từng thành viên:

### Họ tên — MSSV
Nguyễn Minh Đức — 2A202602783
## C2. Self-reflection của từng thành viên

**Thành viên:** Nguyễn Minh Đức
- **Vai trò/phần việc được nhận:** Vai trò B (Tool & Schema Engineer) - Đảm nhiệm việc rà soát và chuẩn hóa kiến trúc Schema cho hệ thống công cụ của Agent.
- **Những gì tôi đã thay đổi trong repo chung:**
    * Chuyển đổi toàn bộ cấu hình JSON Schema dư thừa trong các file Python thành định dạng YAML.
- **File hoặc artifact liên quan:**
    * `tools.yaml` (Nguồn chân lý cho toàn bộ cấu trúc Tools)
    * `tools/clarify.py`, `tools/inspect_device.py`, `tools/create_ticket.py` và các file tool khác (nơi đã xóa biến `SCHEMA`).
- **Commit hash hoặc pull request:** 
    * *(Bạn điền mã commit hoặc link PR của bạn vào đây, ví dụ: `commit 8f3a9b2...` hoặc `PR #3`)*
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
    * **Chuẩn hóa và đồng bộ Schema (Source of Truth):** Tôi đã tiến hành rà soát toàn bộ logic Python trong thư mục `tools/` và quyết định xóa bỏ hoàn toàn biến `SCHEMA` nằm rải rác ở cuối các file Python để chuyển đổi sang định dạng YAML, quy tụ chúng về file `tools.yaml`.
    * **Lý do:** Mục tiêu là biến file `tools.yaml` thành cấu hình gốc duy nhất (source of truth) cho Agent. Điều này giải quyết triệt để tình trạng lệch pha (drift) giữa khai báo tham số của Agent và logic code thực thi. Bằng cách này, nhóm Prompt (Vai trò A) và nhóm Test (Vai trò C) có một tài liệu chuẩn duy nhất để tham chiếu, tránh được các lỗi runtime do truyền sai định dạng.
    * *Evidence:* Xem file [tools.yaml](./tools.yaml) đã được cập nhật chuẩn xác.
- **Khó khăn tôi gặp và cách tôi xử lý:**
    Quá trình rà soát phát hiện ra sự bất đồng bộ giữa khai báo enum ban đầu và logic xử lý thực tế trong code Python (ví dụ: tool `clarify` và `inspect_device` có các mảng giá trị enum khác với thiết kế ban đầu). 
    *Cách xử lý:* Tôi phải đọc kỹ logic từng hàm trong các file `.py` (đặc biệt là các câu lệnh `if` kiểm tra tham số đầu vào) để viết lại danh sách `enum` và các trường `required` trong file YAML cho khớp 100% với cách code thực sự hoạt động.
- **Điều tôi học được từ phần việc này:**
    Tôi nhận ra rằng trong việc xây dựng Tool cho LLM, "lời hứa" (khai báo trong Schema) phải khớp tuyệt đối với "thực thi" (code Python). LLM rất dễ sinh ra tham số rác hoặc bị ảo giác nếu Schema không định nghĩa rõ ràng các giới hạn (như default value, required fields, hay enum lists).
- **Nếu làm lại, tôi sẽ cải thiện điều gì:**
    Nếu có thêm thời gian, tôi sẽ viết một đoạn script Python nhỏ chạy trong quá trình CI/CD để tự động đọc file `tools.yaml` và đối chiếu cấu trúc (validate) với các tham số của các hàm Python trong thư mục `tools/`. Việc này sẽ giúp phát hiện ngay lập tức nếu ai đó sửa code mà quên cập nhật YAML.

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [x] `TEAMMATES.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [x] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [x] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [x] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [x] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [x] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [x] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [x] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:
