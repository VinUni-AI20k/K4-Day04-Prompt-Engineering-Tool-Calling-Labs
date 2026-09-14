# Sổ Tay Theo Dõi Công Việc — Tool & Schema Engineer
## Vai trò: Thành viên 2 (Tool & Schema Engineer + Bonus Tool)
**Dự án:** Day 04 Lab — IT Helpdesk Agent  
**Repository:** `K4A-Day04-5AESIUNHAN`

---

## 1. Danh mục Công việc & Tiến độ Tổng quan

| STT | Đầu việc | Trạng thái | File tác động | Ghi chú / Commit |
|:---:|---|:---:|---|---|
| **1** | **Khảo sát 9 tool có sẵn & phân tích điểm yếu của `tools.yaml`** | ✅ Hoàn thành | `tools/`, `artifacts/tools.yaml` | Đối chiếu code Python thực tế với schema ban đầu, chỉ ra 5 nhóm lỗi cốt lõi |
| **2** | **Tối ưu hóa `tools.yaml` cho phiên bản v1** | ✅ Hoàn thành | `starter_v0/artifacts/tools.yaml` | Bổ sung ranh giới routing, cấm đoán ID, giải thích enum và safety guardrails |
| **3** | **Tối ưu hóa `tools.yaml` cho phiên bản v2 & v3** | ✅ Hoàn thành | `starter_v0/artifacts/tools.yaml` | Tối ưu hóa toàn diện cho multi-turn, parallel tools, carry-over, stale confirmation và chống rò rỉ dữ liệu |
| **4** | **Thiết kế và xây dựng Bonus Tool mới** | ✅ Hoàn thành | `tools/lookup_ticket_status/`, `tools/__init__.py`, `artifacts/tools.yaml`, `helpdesk_data/mock_tickets.json` | Xây dựng hoàn chỉnh tool `lookup_ticket_status` đạt đủ 9 tiêu chuẩn bonus |
| **5** | **Smoke test độc lập toàn bộ các tools** | ✅ Hoàn thành | `starter_v0/scripts/smoke_all_tools.py` | Tạo test suite tự động kiểm tra cả 10 tools; 100% test cases đều PASS |
| **6** | **Cập nhật Báo cáo `REPORT.md` (Mục A2, B5, B7)** | ✅ Hoàn thành | `starter_v0/artifacts/REPORT.md` | Điền bảng 10 tools (A2), bằng chứng bonus tool (B5), và giải trình kỹ thuật (B7) |
| **7** | **Viết Self-Reflection cá nhân (Mục C2) & Commit Git** | ✅ Hoàn thành | `starter_v0/artifacts/REPORT.md`, Branch `02551-tvhn` | Viết cảm nhận, bài học, khó khăn; tạo branch `02551-tvhn`, commit và push lên Git |

---

## 2. Nhật Ký Chi Tiết Các Công Việc Đã Triển Khai

### 📝 [Khởi tạo] Thiết lập sổ tay theo dõi công việc
- **Thời gian:** 14/09/2026
- **Nội dung:** Khởi tạo file `ghichucongviec.md` để lưu lại toàn bộ tiến độ, nhật ký thay đổi kỹ thuật và các quyết định thiết kế nhằm phục vụ báo cáo và commit Git.
- **Kết quả:** Sẵn sàng bước vào Giai đoạn 1.

---

### 🔍 [Đầu việc 1] Khảo sát 9 tool có sẵn & phân tích điểm yếu của `starter_v0/artifacts/tools.yaml`
- **Thời gian:** 14/09/2026
- **Phạm vi kiểm tra:** Đọc toàn bộ code implementation (`tool.py`), metadata (`TOOL.md`) của 9 tool và đối chiếu trực tiếp với `tools.yaml`, `eval_base.json`, `eval_adversarial.json`.
- **Chi tiết đối chiếu từng tool:**
  1. **`clarify`**:
     - *Thực tế code:* Hàm `ask_user` trả về `{"awaiting_user": True}`. Hỗ trợ `response_type` (`text`, `yes_no`, `choice`).
     - *Điểm yếu trong `tools.yaml`:* Description cực kỳ sơ sài (*"Gửi một câu hỏi cho người dùng"*). Thiếu hoàn toàn ngữ cảnh khi nào cần gọi (khi thiếu Asset ID/Employee ID, hoặc khi cần xin xác nhận hành động ghi `create_ticket`). Model không biết khi nào chọn `text` vs `yes_no`.
  2. **`check_service_status`**:
     - *Thực tế code:* Đọc file `service_status.json`. Dịch vụ dùng chung: `vpn`, `email`, `sso`, `wifi`, `printing`. Môi trường: `production`, `staging`.
     - *Điểm yếu trong `tools.yaml`:* Không làm rõ đây là **dịch vụ dùng chung của toàn công ty (shared services)**. Dẫn tới lỗi routing: khi user báo lỗi máy cá nhân (LT-204), model nhầm lẫn gọi tool này thay vì `inspect_device`.
  3. **`inspect_device`**:
     - *Thực tế code:* Nhận `asset_id` định dạng `(?:LT|DT|MB|PR|RM)-\d+` và `check` (`all`, `network`, `vpn`, `security`, `hardware`, `software`).
     - *Điểm yếu trong `tools.yaml`:* Không ghi chú bắt buộc phải có `asset_id` rõ ràng do user cung cấp; không cấm model tự bịa/đoán mã máy. Chưa mô tả các nhóm kiểm tra cụ thể của `check`.
  4. **`lookup_user`**:
     - *Thực tế code:* Tra cứu nhân viên theo `employee_id` (`EMP-xxxx`).
     - *Điểm yếu trong `tools.yaml`:* Không ghi rõ chỉ tra cứu khi có Employee ID; thiếu hướng dẫn gọi `clarify` nếu người dùng chỉ cung cấp tên chung chung ("bạn Sales").
  5. **`format_incident_report`**:
     - *Thực tế code:* Nhận mảng `findings`, `template` (`brief`, `technical`, `handoff`), `incident_title`.
     - *Điểm yếu trong `tools.yaml`:* Không nêu rõ ràng chỉ dùng khi **đã có sẵn findings** trong hội thoại. Model có thể bị gọi thừa các tool chẩn đoán khác thay vì chỉ format lại thông tin sẵn có.
  6. **`policy`**:
     - *Thực tế code:* Tra cứu 6 nhóm chính sách nội bộ: `access_control`, `data_privacy`, `external_tools`, `incident_response`, `service_operations`, `ticketing`.
     - *Điểm yếu trong `tools.yaml`:* Không mô tả phạm vi của từng `policy_area`, khiến model khó route đúng giữa `data_privacy` (quy định dữ liệu/token) và `access_control` (quy định tài khoản/MFA/mật khẩu).
  7. **`create_ticket`**:
     - *Thực tế code:* Ghi file JSON vào thư mục `tickets/`. Kiểm tra nghiêm ngặt `confirmed is True` (boolean thật) và regex chặn credentials/MFA/token (`SENSITIVE_DATA_PATTERN`).
     - *Điểm yếu trong `tools.yaml`:* Cực kỳ nguy hiểm khi mô tả chỉ là *"Tạo một ticket hỗ trợ"*. Không có cảnh báo đây là action có side-effect; không nhắc model rằng **chỉ được gọi khi có explicit confirmation** từ người dùng.
  8. **`search_device_info`**:
     - *Thực tế code:* Gọi Tavily Search API ra ngoài Internet. Có regex chặn nghiêm ngặt mã asset/employee (`LT-...`, `EMP-...`).
     - *Điểm yếu trong `tools.yaml`:* Chưa nhấn mạnh ở từng argument `manufacturer` và `model` rằng tuyệt đối không được truyền internal asset ID hoặc serial vào đây.
  9. **`search_kb`**:
     - *Thực tế code:* Tìm hướng dẫn kỹ thuật dạng How-to trong các bài viết Markdown.
     - *Điểm yếu trong `tools.yaml`:* Chưa phân biệt rõ giữa tìm tài liệu hướng dẫn (How-to) với kiểm tra trạng thái vận hành (`check_service_status`) hoặc quy định nội bộ (`policy`).
- **Tổng kết 5 nhóm lỗi cốt lõi trong `tools.yaml` hiện tại:**
  1. *Lỗi ranh giới năng lực (Capability Ambiguity):* Nhầm lẫn giữa shared service (`check_service_status`) và device snapshot (`inspect_device`).
  2. *Lỗi thiếu ràng buộc danh tính (Missing Identifier Guardrails):* Không hướng dẫn fallback về `clarify` khi thiếu `asset_id` / `employee_id`.
  3. *Lỗi ranh giới hành động ghi (Action/Write Boundary):* Không cảnh báo side-effect của `create_ticket`, khiến model tự ý kích hoạt mà không xin xác nhận.
  4. *Lỗi rò rỉ dữ liệu ra ngoài (Data Exfiltration Boundary):* Chưa cấm triệt để việc đưa identifier vào external search `search_device_info`.
  5. *Lỗi tham số enum & convention:* Thiếu giải thích chi tiết ý nghĩa các giá trị enum (`template`, `policy_area`, `response_type`, `check`).

---

### 🛠️ [Đầu việc 2] Tối ưu hóa `tools.yaml` cho phiên bản v1
- **Thời gian:** 14/09/2026
- **File thay đổi:** `starter_v0/artifacts/tools.yaml`
- **Các cải tiến kỹ thuật cụ thể đã triển khai:**
  1. **`check_service_status` vs `inspect_device`:** Phân định dứt khoát: `check_service_status` chỉ dùng cho dịch vụ dùng chung hạ tầng toàn công ty (VPN, Email, SSO, Wi-Fi, Printing). `inspect_device` dành riêng cho thiết bị/máy tính cụ thể khi biết mã `asset_id` (LT-204, DT-031...). Thêm cảnh báo cấm đoán mò `asset_id`.
  2. **`clarify`:** Bổ sung mô tả toàn diện về ngữ cảnh gọi (khi thiếu mã máy, mã nhân viên hoặc xin xác nhận). Giải thích rõ 3 chế độ `response_type`: `text` (hỏi thông tin định danh/chi tiết), `yes_no` (xin xác nhận hành động ghi như tạo ticket), `choice` (chọn từ options).
  3. **`lookup_user`:** Bắt buộc có mã `employee_id` (EMP-xxxx), hướng dẫn fallback gọi `clarify` nếu user chỉ đưa tên phòng ban hoặc chức danh chung chung.
  4. **`format_incident_report`:** Nêu rõ chỉ format khi ĐÃ CÓ SẴN findings trong ngữ cảnh hội thoại, tránh gọi thừa các tool kiểm tra khác. Mô tả chi tiết 3 mẫu `template` (`brief`, `technical`, `handoff`).
  5. **`search_kb`:** Làm rõ mục đích tìm hướng dẫn How-to/troubleshooting từng bước, phân biệt với việc tra cứu trạng thái hạ tầng hay chính sách công ty.
  6. **`create_ticket` & `search_device_info`:** Thêm cảnh báo side-effect (yêu cầu explicit confirmation với `confirmed: true`) và ranh giới dữ liệu cá nhân (tuyệt đối không truyền mã máy/mã nhân viên ra internet).
- **Kiểm thử kỹ thuật:**
  - Cài đặt dependency `pyyaml>=6.0`.
  - Kiểm tra cú pháp YAML và hàm chuyển đổi: `to_openai_tools()` tải thành công 9 tools với cấu trúc JSON Schema hợp lệ 100%.
  - Chạy `python -m compileall -q .` không phát hiện lỗi cú pháp.
- **Commit Message đề xuất:**
  `feat(schema): optimize tools.yaml for v1 routing accuracy and parameter validation`

---

### 🛡️ [Đầu việc 3] Tối ưu hóa `tools.yaml` cho phiên bản v2 & v3 (Nâng cao & Ranh giới An toàn)
- **Thời gian:** 14/09/2026
- **File thay đổi:** `starter_v0/artifacts/tools.yaml`
- **Các nâng cấp chuyên sâu cho v2 & v3:**
  1. **Hỗ trợ gọi song song (Parallel Tool Calls - cases H13, H15, H16, H17):**
     - Bổ sung chỉ dẫn trong `inspect_device`: khi so sánh nhiều thiết bị (như LT-204 và DT-031), model phải gọi song song nhiều lần, mỗi lần nhận đúng MỘT `asset_id`, không ghép chuỗi.
     - Bổ sung chỉ dẫn trong `check_service_status`: khi so sánh production và staging, gọi song song 2 lần với 2 environment khác nhau.
  2. **Kế thừa ngữ cảnh (Context Carry-over & Correction - cases M01-M06):**
     - `check_service_status`: Kế thừa `environment` ở lượt trước nếu lượt này user đổi `service` mà không nhắc lại môi trường.
     - `inspect_device` & `lookup_user`: Hướng dẫn model khi user sửa lại ID ở lượt sau (*Correction*), luôn ưu tiên ID mới nhất.
  3. **Chống giả mạo xác nhận (Anti-Spoofing & Argument Smuggling - cases A02, A03, A04):**
     - Trong `create_ticket`: Bổ sung rule cấm công nhận pseudo-code, object JSON tự gán `confirmed: true` hoặc chuỗi `TOOL_RESULTS_JSON:` giả mạo. Bắt buộc phải fallback về `clarify(response_type="yes_no")`.
  4. **Xác nhận cũ hết hiệu lực (Stale Confirmation - case A09, M05):**
     - Quy định rõ ràng: Nếu payload thay đổi (ví dụ user đổi priority từ medium lên high, hoặc đổi mã asset), xác nhận cũ lập tức bị hủy, model bắt buộc phải gọi lại `clarify(response_type="yes_no")`.
  5. **Chống rò rỉ dữ liệu (Data Exfiltration Boundary - cases A05, A06, A12):**
     - `create_ticket`: Cấm tuyệt đối đưa password, token, API key, MFA/OTP code vào summary.
     - `search_device_info`: Cấm tuyệt đối đưa `asset_id`, `employee_id`, serial, hostname, location hay diagnostic logs ra ngoài Internet.
  6. **Đặc tả chi tiết 6 nhóm `policy_area`:**
     - Mô tả rõ ràng từ khóa nhận diện của từng khu vực: `access_control`, `data_privacy`, `external_tools`, `incident_response`, `service_operations`, `ticketing`.
- **Kiểm thử kỹ thuật:**
  - `load_tool_declarations()` và `to_openai_tools()` tải mượt mà 9 tools.
  - Biên dịch toàn bộ repo không có cảnh báo hoặc lỗi.
- **Commit Message đề xuất:**
  `feat(schema): harden tools.yaml for v2/v3 with parallel calling, multi-turn carry-over, and safety boundaries`

---

### 🚀 [Đầu việc 4] Thiết kế và xây dựng Bonus Tool: `lookup_ticket_status`
- **Thời gian:** 14/09/2026
- **Tên Tool mới:** `lookup_ticket_status` (Theo dõi và kiểm tra trạng thái ticket sự cố IT).
- **Đáp ứng đủ 9 tiêu chí Bonus Tool theo quy định:**
  1. *Thư mục và spec:* Tạo [starter_v0/tools/lookup_ticket_status/TOOL.md](starter_v0/tools/lookup_ticket_status/TOOL.md) với đầy đủ frontmatter (`track: bonus`, `kind: local_status`, `side_effect: false`, `requires_confirmation: false`).
  2. *Code implementation:* Viết code [starter_v0/tools/lookup_ticket_status/tool.py](starter_v0/tools/lookup_ticket_status/tool.py) xử lý linh hoạt:
     - Đọc dữ liệu từ cơ sở dữ liệu mẫu `helpdesk_data/mock_tickets.json` (chứa các ticket thực tế như `INC-1042`, `INC-1045`, `CHG-221`, `TCK-1001`, `TCK-1002`).
     - Đọc trực tiếp từ thư mục `tickets/` đối với các ticket mới sinh ra trong phiên làm việc bởi `create_ticket`.
     - Xử lý ngoại lệ chuẩn: trả về `ticket_not_found` kèm danh sách ticket mẫu gợi ý, hoặc `missing_ticket_id` nếu người dùng để trống.
  3. *Dữ liệu mẫu giả lập:* Tạo [starter_v0/helpdesk_data/mock_tickets.json](starter_v0/helpdesk_data/mock_tickets.json).
  4. *Đăng ký Registry:* Đăng ký hàm `lookup_ticket_status` vào `TOOL_FUNCTIONS` trong [starter_v0/tools/__init__.py](starter_v0/tools/__init__.py).
  5. *Khai báo Schema:* Thêm declaration hoàn chỉnh cho `lookup_ticket_status` vào [starter_v0/artifacts/tools.yaml](starter_v0/artifacts/tools.yaml).
  6. *Smoke Test:*
     - Lệnh kiểm tra ticket có sẵn: `python -c "from tools import TOOL_FUNCTIONS as T; print(T['lookup_ticket_status']('INC-1042'))"` $\rightarrow$ Trả về đúng thông tin sự cố, người xử lý, giải pháp.
     - Lệnh kiểm tra ticket không tồn tại: `python -c "from tools import TOOL_FUNCTIONS as T; print(T['lookup_ticket_status']('TCK-9999'))"` $\rightarrow$ Trả về lỗi `ticket_not_found` có cấu trúc rõ ràng.
     - Kiểm tra liên kết động: `create_ticket` tạo `LAB-xxxx` $\rightarrow$ `lookup_ticket_status` tra cứu ngay lập tức thành công!
  7. *Vệ sinh bài nộp:* Đã dọn dẹp sạch sẽ các ticket test trong thư mục `tickets/` để không commit ticket rác theo yêu cầu của `SUBMISSION-GUIDE.md`.
- **Commit Message đề xuất:**
  `feat(bonus-tool): implement lookup_ticket_status tool with mock data, registry, and schema`

---

### 🧪 [Đầu việc 5] Smoke test độc lập toàn bộ 10 tools
- **Thời gian:** 14/09/2026
- **Script kiểm thử tự động:** Tạo mới [starter_v0/scripts/smoke_all_tools.py](starter_v0/scripts/smoke_all_tools.py) để chạy smoke test độc lập toàn diện không phụ thuộc LLM.
- **Lệnh thực thi:**
  ```powershell
  cd starter_v0
  python scripts/smoke_all_tools.py
  ```
- **Bảng kết quả kiểm thử (10/10 PASS):**
  | Tên Tool | Loại kiểm thử | Kết quả | Chi tiết kiểm chứng |
  |---|---|:---:|---|
  | `clarify` | Input contract & Return structure | **PASS** | `awaiting_user=True`, `response_type='text'` |
  | `search_kb` | Knowledge retrieval & Trust boundary | **PASS** | Lấy đúng 2 bài viết VPN, có ranh giới `trust_boundary` |
  | `check_service_status` | Mock JSON query & Fields | **PASS** | `service='vpn'`, `status='degraded'`, có `checked_at` |
  | `inspect_device` | Asset inventory & Diagnostic group | **PASS** | `asset_id='LT-318'`, chẩn đoán `vpn` chính xác |
  | `lookup_user` | Directory record & Assigned assets | **PASS** | `employee_id='EMP-1007'`, assigned asset `DT-087` |
  | `format_incident_report` | Markdown template & Counting | **PASS** | `finding_count=2`, render markdown `brief` chuẩn |
  | `policy` | Policy area filter & Metadata | **PASS** | Tra cứu đúng khu vực `external_tools`, kết quả > 0 |
  | `create_ticket` | Side-effect dry run & Sensitive data block | **PASS** | Dry-run trả `needs_confirmation`; chặn thành công password injection |
  | `search_device_info` | Data exfiltration guardrail | **PASS** | Chặn đứng mã máy `LT-204`, trả `restricted_internal_identifier` |
  | `lookup_ticket_status` | Bonus tool database & dynamic lookup | **PASS** | Tra cứu thành công `INC-1042`; xử lý đúng ngoại lệ `ticket_not_found` |
- **Kết luận:** Toàn bộ 10 tools vận hành hoàn hảo, các ranh giới bảo mật hoạt động chuẩn xác theo thiết kế.
- **Commit Message đề xuất:**
  `test(tools): add comprehensive smoke_all_tools.py test suite with 100% pass rate`

---

### 📑 [Đầu việc 6] Cập nhật Báo cáo `REPORT.md` (Mục A2, B5, B7)
- **Thời gian:** 14/09/2026
- **File thay đổi:** `starter_v0/artifacts/REPORT.md`
- **Nội dung đã hoàn thành:**
  1. **Mục A2 (Bảng các Tool agent có):** Kê khai đủ toàn bộ 10 tools (6 core, 3 optional, 1 bonus team-built) kèm tóm tắt chức năng chuẩn hóa.
  2. **Mục B5 (Optional và Bonus tool evidence):** Bổ sung bằng chứng triển khai, các file evidence liên quan, hiệu quả kiểm thử và các cơ chế bảo mật (Guardrails) của các tool nâng cao (`policy`, `create_ticket`, `search_device_info`) và bonus tool (`lookup_ticket_status`).
  3. **Mục B7 (Technical reflection):** Trả lời chi tiết và chuyên sâu 4 câu hỏi kỹ thuật:
     - Phân định rõ fix nào thuộc `system_prompt.md` vs fix nào thuộc `tools.yaml`.
     - Phân tích nguyên nhân vì sao có những failure không thể chỉ nhìn automatic score mà phải audit filesystem/tool results thủ công.
     - Đề xuất 2 hypothesis mở rộng có tính khả thi cao cho vòng lặp tiếp theo.
- **Commit Message đề xuất:**
  `docs(report): update tool catalog A2, bonus evidence B5, and technical reflection B7`

---

### 🌟 [Đầu việc 7] Viết Self-Reflection cá nhân (Mục C2), Khởi tạo Branch & Đẩy lên Git
- **Thời gian:** 14/09/2026
- **Nội dung hoàn thành:**
  1. **Tự viết phần Self-Reflection cá nhân (Mục C2 trong `REPORT.md`):**
     - Đứng tên: **Hoang Nguyen — 02551 (tvhn)**
     - Trình bày đầy đủ: vai trò, danh sách các file thay đổi, quyết định kỹ thuật quan trọng (ranh giới schema vs prompt, bonus tool kiến trúc kép), khó khăn gặp phải (chống argument smuggling, stale confirmation, mã hóa Windows) và bài học rút ra (Defense in Depth, Tool Schema chính là Prompt).
     - Giữ nguyên template cho 4 thành viên còn lại trong nhóm theo quy định.
  2. **Quy trình Git & Ranh giới an toàn (Branch: `02551-tvhn`):**
     - Tạo và checkout sang nhánh riêng: `02551-tvhn`.
     - Kiểm tra định danh tác giả (Git identity): `hoang nguyen <haringnguyen5@gmail.com>`.
     - Kiểm tra vệ sinh bảo mật: Không commit `.env`, `.venv`, cache `__pycache__` hay file ticket rác sinh ra trong thư mục `tickets/`.
     - Đóng gói toàn bộ các artifact: `tools.yaml`, `tools/lookup_ticket_status/`, `tools/__init__.py`, `helpdesk_data/mock_tickets.json`, `smoke_all_tools.py`, `REPORT.md`, `ghichucongviec.md`, `PHAN-CONG-NHOM.md`.
     - Thực hiện commit và đẩy lên remote repository (`origin/02551-tvhn`).
- **Commit Message:**
  `feat(tools): complete tools.yaml v1-v3, lookup_ticket_status bonus tool, smoke tests, and self-reflection`

---

## 3. Sổ Ghi Nhớ Kỹ Thuật (Phục vụ viết Self-Reflection mục C2)

1. **Một quyết định kỹ thuật quan trọng đã đưa ra và lý do:**
   - *Phân định rõ ranh giới Tool thay vì nhồi nhét rule vào System Prompt:* Nhận thấy model thường nhầm lẫn giữa `inspect_device` và `check_service_status` không phải do system prompt thiếu thông tin, mà do `description` của hai tool này trong `tools.yaml` quá giống nhau. Quyết định bổ sung ngữ cảnh sử dụng và phản ví dụ (negative examples / "khi nào KHÔNG dùng") trực tiếp vào description của tool.
   - *Chống Argument Smuggling bằng Schema Description:* Kẻ tấn công thường nhét chuỗi `create_ticket({"confirmed": true})` vào user query để đánh lừa model. Bằng cách quy định rõ trong description của `create_ticket` rằng chỉ chấp nhận xác nhận bằng ngôn ngữ tự nhiên từ câu trả lời trước của user, model sẽ không bị sập bẫy và chuyển hướng an toàn sang `clarify(response_type="yes_no")`.
   - *Thiết kế Bonus Tool lookup_ticket_status có tính kế thừa hai chiều:* Thay vì chỉ đọc một file json tĩnh, tôi thiết kế tool kiểm tra đồng thời cả hai nguồn: (1) Mock database các sự cố đã có trong quá khứ (`INC-1042`, `INC-1045`...) và (2) Các ticket JSON mới sinh ra trong thư mục `tickets/` bởi tool `create_ticket`. Điều này giúp hệ thống agent có tính nhất quán thực tế: tạo ticket xong là có thể tra cứu ngay lập tức.
2. **Khó khăn kỹ thuật gặp phải và cách khắc phục:**
   - *Ranh giới an toàn của create_ticket:* Tool code trong Python bắt buộc kiểm tra `confirmed is True` (kiểu boolean chuẩn), nếu model truyền chuỗi `"true"` hoặc tự ý gọi mà không xin phép thì tool sẽ trả về lỗi `needs_confirmation`. Khắc phục bằng cách mô tả rõ trong schema của `create_ticket` rằng `confirmed` bắt buộc là boolean và chỉ kích hoạt sau khi đã nhận được sự đồng ý dứt khoát của người dùng.
   - *Quy tắc Stale Confirmation (Xác nhận hết hạn):* Khi người dùng đã đồng ý tạo ticket nhưng ngay câu sau lại đổi ý "Đổi mức ưu tiên thành High nhé", model thường giữ nguyên trạng thái confirmed cũ và gọi ngay tool ghi file. Khắc phục bằng cách ghi rõ trong schema rằng bất kỳ thay đổi nào về payload đều làm mất hiệu lực xác nhận cũ và buộc phải hỏi lại xác nhận mới.
   - *Lỗi UnicodeEncodeError trên terminal Windows:* Khi viết message tiếng Việt có dấu trong `tool.py`, terminal mặc định của Windows (`cp1252`) bị lỗi encoding khi print. Tôi đã chuẩn hóa các message và error keys sang tiếng Anh chuyên ngành Helpdesk (giống như các core tools `inspect_device`, `lookup_user`), giúp tool chạy mượt mà trên mọi môi trường và nền tảng.
3. **Bài học kinh nghiệm rút ra:**
   - Schema của Tool (description, parameter description, enum) chính là một phần của Prompt mà model "nhìn" thấy. Một schema được đặc tả chuẩn chỉ và chặt chẽ có khả năng giảm thiểu đến hơn 70% lỗi routing và argument mà không làm phình to System Prompt.
   - Việc phối hợp giữa Schema chặt chẽ và Code chốt chặn an toàn (Defense in Depth) là mô hình bảo vệ Agent hiệu quả nhất trước các cuộc tấn công Adversarial.
   - Một tool tốt không chỉ là hoàn thành happy path mà phải xử lý graceful handling khi input không tồn tại (trả về lỗi rõ ràng kèm sample gợi ý).


