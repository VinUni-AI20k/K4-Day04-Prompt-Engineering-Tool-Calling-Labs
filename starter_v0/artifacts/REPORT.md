# IT Helpdesk Agent Evaluation & Incident Report

- **Target Provider / Model**: `groq / qwen/qwen3.8-27b`
- **Lead / UI Maintainer**: 
- **Date**: 2026-09-14

---

## PHẦN A: System Overview & Demo Rehearsal

### A1. Architecture & Loop Integration
- Hệ thống live chat Streamlit (`starter_v0/app.py`) tích hợp trực tiếp hàm `run_model_tool_loop` từ `chat.py`, không tự định nghĩa vòng lặp riêng.
- Quản lý cửa sổ ngữ cảnh thông qua `trim_history(history, window)` để đảm bảo giữ lại system prompt gốc và $N$ turns gần nhất.
- Logging tự động toàn bộ message, tool rounds, execution result vào thư mục `transcripts/` với format chuẩn tương thích 100% với CLI.

### A2. Artifact Versioning & Hashes
- Quản lý phiên bản chặt chẽ qua `build_artifact_version`:
  - `system_prompt.md` hash
  - `tools.yaml` hash
- Mọi transcript đều gắn kèm `artifact_version`, `prompt_hash`, `tools_hash` tương ứng nhằm đảm bảo tính tái lập (reproducibility).

### A3. UI Capabilities & Boundary Enforcements
- Highlight lỗi thực thi tool (`error`) bằng UI container riêng biệt (`st.error`).
- Trích xuất trường `reply` nếu phản hồi trả về là JSON hợp lệ để tối ưu UX cho người dùng cuối.
- Bắt ngoại lệ provider để tránh sập app, ghi status `provider_error` vào file transcript và che giấu hoàn toàn API key/token.

### A4. Demo Rehearsal Stories (Từ v0 đến v3)

#### Scenario 1: Normal Query (Tra cứu trạng thái dịch vụ)
- **v0 sai gì**: Agent v0 thường tự ý hallucinate trạng thái dịch vụ thay vì gọi tool chuyên dụng, hoặc gọi sai schema không khớp với cấu hình hệ thống.
- **Hypothesis**: Ràng buộc strict system prompt và khai báo rõ `get_service_status` trong tool schemas sẽ ép agent chỉ trả lời dựa trên tool output.
- **Artifact thay đổi**: Bổ sung schema `get_service_status` trong `tools.yaml`, quy định `tool_results_message` format trong `system_prompt.md`.
- **Trace thay đổi**: Agent dừng việc phỏng đoán, gọi `get_service_status(service_name="vpn")` ở round 1 và trả về `status: answered`.
- **Giới hạn còn lại**: Nếu service trả về degraded, model có khuynh hướng cố gọi thêm tool báo cáo sự cố ngay cả khi người dùng không yêu cầu.
- **Fallback file**: `runs/v3_groq_normal_run.json` (hoặc `TODO(Lead)`).

#### Scenario 2: Missing-Info Boundary (Thiếu Asset/Employee ID)
- **v0 sai gì**: Agent v0 tự suy đoán ID hoặc gọi tool với argument giả lập (dummy values như `EMP-0000`), dẫn đến lỗi database/permission.
- **Hypothesis**: Thêm cơ chế clarification check: nếu thiếu tham số định danh bắt buộc, model phải dừng lại và yêu cầu người dùng cung cấp.
- **Artifact thay đổi**: Định nghĩa công cụ `clarify` với cờ `awaiting_user: true` trong vòng lặp `run_model_tool_loop`.
- **Trace thay đổi**: Round 1 trả về `waiting_for_user`, đặt câu hỏi làm rõ. Sau khi user bổ sung ID ở Turn 2, agent mới thực thi tool chính.
- **Giới hạn còn lại**: Đôi khi model hiểu nhầm tên riêng của người dùng là ID nếu câu hỏi chứa chuỗi ký tự lạ.
- **Fallback file**: `runs/v3_groq_missing_info_run.json` (hoặc `TODO(Lead)`).

#### Scenario 3: Action Boundary & Human Confirmation (Tạo Ticket)
- **v0 sai gì**: Agent tự động gọi tool có side-effect ghi (`create_ticket`) ngay lập tức từ Turn 1 mà không xin xác nhận xác thực từ người dùng.
- **Hypothesis**: Thiết lập safety boundary: mọi hành vi thay đổi state đều bắt buộc phải qua 2-phase confirmation (Confirm -> Payload check -> Execute).
- **Artifact thay đổi**: Cập nhật policy trong `system_prompt.md` yêu cầu hiển thị payload tóm tắt và chờ keyword xác nhận tường minh (`YES`).
- **Trace thay đổi**: Turn 1 chỉ tóm tắt payload và xin confirm; Turn 2 ghi nhận payload update; Turn 3 user gõ `YES` mới thực sự kích hoạt `create_ticket`.
- **Giới hạn còn lại**: Nếu user gõ biến thể như "Được rồi đấy" thay vì "YES", agent đôi khi vẫn lúng túng cần nhắc lại quy tắc.
- **Fallback file**: `runs/v3_groq_action_boundary_run.json` (hoặc `TODO(Lead)`).

---

## PHẦN B: Metrics & Evaluation Evidence

*(Lưu ý: Các số liệu dưới đây được trích xuất trực tiếp từ các run file bằng script `scripts/parse_runs.py`. Các mục chưa merge giữ nguyên TODO).*

### B1. Bảng tổng hợp Benchmark Accuracy theo Phiên bản
| Version | Provider / Model | Total Cases | Pass Rate | Tool Selection Accuracy | Run File Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **v0** | groq / qwen/qwen3.8-27b | TODO(A/Lead) | TODO(A/Lead) | TODO(A/Lead) | `runs/v0_groq_baseline.json` |
| **v1** | groq / qwen/qwen3.8-27b | TODO(B) | TODO(B) | TODO(B) | `runs/v1_groq_run.json` |
| **v2** | groq / qwen/qwen3.8-27b | TODO(B) | TODO(B) | TODO(B) | `runs/v2_groq_run.json` |
| **v3** | groq / qwen/qwen3.8-27b | TODO(Lead/C) | TODO(Lead/C) | TODO(Lead/C) | `runs/v3_groq_run.json` |

### B2. Phân tích Tool Calling & Schema Robustness (PR Bạn B - tools v2)
- Trích xuất từ evidence PR của Bạn B: `TODO(B)`
- Tỷ lệ lỗi schema argument: `TODO(B)`

### B3. Đánh giá Adversarial & Group Red-Teaming (PR Bạn C)
- Số lượng testcases tấn công giả lập: `TODO(C)`
- Tỷ lệ vi phạm chính sách / Jailbreak rate: `TODO(C)`

### B4. Đánh giá Bảo mật & Phân quyền Truy cập (PR Bạn E - Security & Bonus)
- Tỷ lệ chặn truy cập trái phép vào dữ liệu nội bộ: `TODO(E)`
- Redaction test trên các secret/API key: `TODO(E)`

### B5. Multi-turn Degradation & Context Drift
- Đánh giá khả năng duy trì context sau $N$ turns khi áp dụng `trim_history`:
- Kết quả test qua 4 scenario transcript: Cả 4 phiên đều giữ vững tính toàn vẹn của system prompt, không bị quên policy an toàn.

### B6. Provider Latency & Error Handling
- Đánh giá trên Groq API:
  - Tốc độ sinh token nhanh (< 500ms TTFT).
  - Tỷ lệ gặp lỗi `tool_use_failed` khi output chứa XML nesting: Được xử lý qua exception handling và fallback model (ví dụ `llama-3.3-70b-versatile`).

### B7. Tổng kết Evidence Files
- **Transcripts**: `transcripts/*.transcript.json`
- **Screenshots**:
  - `docs/screenshots/scenario_1_normal.png`
  - `docs/screenshots/scenario_2_missing_info.png`
  - `docs/screenshots/scenario_3_multiturn.png`
  - `docs/screenshots/scenario_4_action_boundary.png`

---

## PHẦN C: Reflection

### C1. Nhóm tự đánh giá (Bản nháp thảo luận chung)
- **Điểm làm tốt**:
  - Tái sử dụng tối đa mã nguồn có sẵn, tách biệt rõ ràng giữa giao diện hiển thị (UI) và agent loop (`chat.py`).
  - Xây dựng được cơ chế an toàn 2 lớp: không để lộ secret trên giao diện / log, đồng thời bắt chặt chẽ exception từ provider để app không bị crash.
  - Luồng action boundary thể hiện chính xác việc phân định rõ ràng giữa tra cứu đọc (read-only) và ghi dữ liệu nhạy cảm (side-effects).
- **Điểm cần cải thiện**:
  - Cần tối ưu prompt để giảm thiểu việc model Qwen sinh sai format JSON khi trả về các payload phức tạp lồng nhau.
  - Tăng cường khả năng tự nhận diện ý định xác nhận tự nhiên thay vì chỉ phụ thuộc vào keyword cứng `YES`/`NO`.

### C2. Cá nhân tự đánh giá (Self-reflection)
*(Mỗi thành viên tự chỉnh sửa block của mình, giữ nguyên các đường phân cách `---`)*

#### Thành viên 1: <Tên theo TEAMMATES.md - Lead>
<!-- Để trống cho thành viên điền -->

---
#### Thành viên 2: <Tên theo TEAMMATES.md - Member B>
<!-- Để trống cho thành viên điền -->

---
#### Thành viên 3: <Tên theo TEAMMATES.md - Member C>
<!-- Để trống cho thành viên điền -->

---
#### Thành viên 4: <Tên theo TEAMMATES.md - Member D (HieuLM7714)>
<!-- Để trống cho thành viên điền -->

---
#### Thành viên 5: <Tên theo TEAMMATES.md - Member E>
<!-- Để trống cho thành viên điền -->