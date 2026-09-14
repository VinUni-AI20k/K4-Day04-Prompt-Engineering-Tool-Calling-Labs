# Kế hoạch Phân công Công việc & Quy trình Git (Nhóm 5 người)
## IT Helpdesk Agent — Day 04 Lab

Tài liệu này được biên soạn để phân định rõ phạm vi trách nhiệm giữa 5 thành viên, giúp **tránh hoàn toàn xung đột Git (merge conflict)** và đảm bảo **100% thành viên đều có commit riêng hợp lệ** trên repository nộp bài theo quy định của [SUBMISSION-GUIDE.md](SUBMISSION-GUIDE.md).

---

## 1. Bảng phân công tổng quan

| STT | Thành viên | Vai trò | File/Thư mục phụ trách độc quyền | Output / Bằng chứng commit bắt buộc |
|:---:|---|---|---|---|
| **1** | **Thành viên 1** *(Lead)* | **Prompt Architect & Quản trị Repo** | • `TEAMMATES.md`<br>• `starter_v0/artifacts/system_prompt.md`<br>• `starter_v0/artifacts/version_log.csv` | • Commit tạo `TEAMMATES.md`<br>• Commit prompt qua các version (v1 → v3)<br>• Commit kết quả run baseline `v0` |
| **2** | **Thành viên 2** | **Tool & Schema Engineer** *(+ Bonus Tool)* | • `starter_v0/artifacts/tools.yaml`<br>• Thư mục tool mới `starter_v0/tools/<new_tool>/` *(nếu làm bonus)* | • Commit chuẩn hóa mô tả/schema trong `tools.yaml`<br>• Commit code implementation & `TOOL.md` của Bonus Tool |
| **3** | **Thành viên 3** | **Eval & Test Designer** | • `starter_v0/data/eval_group.json`<br>• Chạy suite Group | • Commit 10 test cases trong `eval_group.json`<br>• Commit file run kết quả của group eval |
| **4** | **Thành viên 4** | **UI & Chat Engineer** | • `starter_v0/app.py` *(tạo mới)*<br>• `starter_v0/requirements.txt`<br>• Lưu transcript / ảnh demo | • Commit tạo `app.py` (Streamlit UI)<br>• Commit cập nhật `requirements.txt`<br>• Commit file transcript chat live |
| **5** | **Thành viên 5** | **Security & Báo cáo viên (Report Lead)** | • `starter_v0/artifacts/REPORT.md`<br>• Chạy suite Adversarial | • Commit phân tích 3 security cases<br>• Commit sườn báo cáo chính `REPORT.md`<br>• Commit kết quả run adversarial suite |

---

## 2. Chi tiết nhiệm vụ từng thành viên

### Thành viên 1: Trưởng nhóm — Prompt Architect & Điều phối
- **Trách nhiệm chính**:
  1. Tạo file `TEAMMATES.md` tại thư mục gốc của repository, điền đầy đủ thông tin của 5 thành viên (Họ tên, MSSV, GitHub username, Vai trò).
  2. Thiết lập môi trường, chạy script preflight (`python scripts/preflight_provider.py --provider <provider>`).
  3. Chạy baseline `v0` với bộ `eval_base.json` (giữ nguyên starter artifacts):
     ```powershell
     python run_eval.py --provider <provider> --version v0 --suite base --eval-cases data/eval_base.json
     ```
  4. Tối ưu [system_prompt.md](starter_v0/artifacts/system_prompt.md) qua các vòng `v1`, `v2`, `v3`:
     - Thiết lập nguyên tắc toàn cục: không tự đoán Asset ID/Employee ID.
     - Xử lý ngữ cảnh đa lượt (ưu tiên thông tin mới nhất).
     - Bắt buộc xác nhận trước các action thay đổi dữ liệu (`create_ticket`).
     - Định dạng output JSON chuẩn (`intent`, `action`, `reply`, `evidence_ids`).
  5. Cập nhật và lưu lại lịch sử thay đổi vào [version_log.csv](starter_v0/artifacts/version_log.csv).
- **Quy tắc tránh conflict**: Chỉ Thành viên 1 chỉnh sửa file `system_prompt.md` và `TEAMMATES.md`.

---

### Thành viên 2: Tool & Schema Engineer (+ Bonus Tool nếu có)
- **Trách nhiệm chính**:
  1. Đọc kỹ implementation của 9 tools trong `starter_v0/tools/`.
  2. Chuẩn hóa file [tools.yaml](starter_v0/artifacts/tools.yaml):
     - Viết mô tả rõ ràng phạm vi sử dụng của từng tool để model không chọn nhầm.
     - Phân định rõ: `check_service_status` (trạng thái hệ thống chung) vs `inspect_device` (chẩn đoán thiết bị cụ thể).
     - Định nghĩa kiểu dữ liệu arguments, enum values, required fields chuẩn xác.
  3. *(Tùy chọn - Điểm Bonus)* Xây dựng 1 tool mới độc lập (ví dụ `tools/lookup_ticket_status/` hoặc `tools/network_diagnostics/`):
     - Viết file `TOOL.md` đầy đủ frontmatter.
     - Viết file `tool.py` chạy độc lập với mock data.
     - Đăng ký vào `tools/__init__.py` và khai báo trong `tools.yaml`.
- **Quy tắc tránh conflict**: Chỉ Thành viên 2 chỉnh sửa `tools.yaml` và làm việc trong thư mục tool bonus riêng.

---

### Thành viên 3: Test & Evaluation Designer
- **Trách nhiệm chính**:
  1. Thiết kế và viết đúng **10 test cases gốc (original cases)** vào file [eval_group.json](starter_v0/data/eval_group.json):
     - **5 single-turn cases**: ví dụ truy vấn mơ hồ cần làm rõ, format báo cáo, tra cứu thiết bị hợp lệ...
     - **5 multi-turn cases**: sửa sai ở lượt sau (correction), hủy hành động (cancellation), xác nhận hành động, bổ sung ID còn thiếu...
  2. Chạy đánh giá bộ test của nhóm trên phiên bản `v3`:
     ```powershell
     python run_eval.py --provider <provider> --version v3 --suite group --eval-cases data/eval_group.json
     ```
  3. Lưu và commit file kết quả run trong thư mục `runs/`.
- **Quy tắc tránh conflict**: Chỉ Thành viên 3 chỉnh sửa file `eval_group.json`.

---

### Thành viên 4: UI & Chat Experience Engineer
- **Trách nhiệm chính**:
  1. Thêm `streamlit>=1.30.0` vào [requirements.txt](starter_v0/requirements.txt).
  2. Tạo mới file `starter_v0/app.py`:
     - **Bắt buộc**: Tái sử dụng hàm `run_model_tool_loop` từ `chat.py`.
     - Giao diện chat trực quan: Khung hội thoại tin nhắn user & assistant.
     - Hiển thị chi tiết tool trace: tên tool, arguments truyền vào, kết quả trả về hoặc mã lỗi (`tool_results` / `errors`).
     - Hiển thị round/status, phiên bản prompt/tool hiện tại và hash tương ứng.
  3. Chạy giao diện và thực hiện các kịch bản demo:
     - Chụp ảnh giao diện minh họa các kịch bản: thông thường, thiếu thông tin (hỏi lại), multi-turn, xác nhận an toàn trước khi tạo ticket.
     - Xuất transcript chat làm bằng chứng nộp bài.
- **Quy tắc tránh conflict**: Làm việc hoàn toàn trên file mới `app.py`, không sửa các file logic nền tảng.

---

### Thành viên 5: Security Reviewer & Báo cáo viên (Report Lead)
- **Trách nhiệm chính**:
  1. Chạy bộ đánh giá Adversarial (12 cases an toàn bảo mật):
     ```powershell
     python run_eval.py --provider <provider> --version v3 --suite adversarial --eval-cases data/eval_adversarial.json
     ```
  2. Kiểm tra thủ công:
     - Kiểm tra thư mục `starter_v0/tickets/` để đảm bảo không bị ghi trộm file ticket nào trái phép.
     - Kiểm tra các cuộc gọi ra ngoài (`search_device_info`) không chứa dữ liệu nhạy cảm (ID, hostname, serial...).
     - Phân tích ít nhất **3 cases bảo mật** điển hình (Prompt injection, Forged confirmation, Role hijacking).
  3. Khởi tạo và tổng hợp nội dung cho [REPORT.md](starter_v0/artifacts/REPORT.md):
     - Điền Phần A (A1–A4: giới thiệu, bảng tool, câu hỏi mẫu, kịch bản demo).
     - Điền Phần B (B1: tiến trình v0-v3, B2: phân tích lỗi, B3: 10 group cases, B4: chat trace, B4a: 3 adversarial cases, B6: safety review, B7: technical reflection).
     - Viết mục C1: Đoạn Reflection chung của cả nhóm.
     - Tạo sẵn khung 5 mục C2 rỗng để các thành viên tự điền.
- **Quy tắc tránh conflict**: Thành viên 5 dựng khung báo cáo và hoàn thành phần chung trước khi các thành viên khác điền mục C2.

---

## 3. Cách phối hợp để điền Báo cáo cá nhân (Mục C2 trong REPORT.md)

Yêu cầu bắt buộc từ [REPORT.md](starter_v0/artifacts/REPORT.md):
> *"Mỗi thành viên phải tự commit phần self-reflection của mình bằng Git identity tương ứng."*

**Quy trình tránh xung đột:**
1. **Thành viên 5** hoàn thành toàn bộ Phần A, Phần B, C1 và tạo sẵn 5 khung C2 (đặt sẵn tên + MSSV của từng người) trong `REPORT.md`, sau đó merge vào `main`.
2. Sau khi nhánh `main` đã có file `REPORT.md` hoàn chỉnh:
3. Lần lượt từng thành viên (hoặc tạo branch riêng) pull code mới nhất về:
   ```powershell
   git pull origin main
   ```
4. Mở file `REPORT.md`, **chỉ điền đúng phần của mình tại mục C2**, sau đó commit và push:
   ```powershell
   git add artifacts/REPORT.md
   git commit -m "docs(report): add self-reflection for Nguyen Van A"
   git push origin contrib/<github_username>
   ```
5. Tạo Pull Request để Trưởng nhóm merge vào nhánh chính.

---

## 4. Quy tắc Git vàng cho cả nhóm (Bắt buộc tuân thủ)

### Bước 1: Thiết lập danh tính Git chuẩn
Mỗi thành viên chạy lệnh sau trên terminal của mình trước khi làm bài:
```powershell
git config user.name "Họ và Tên Của Bạn"
git config user.email "email_cua_ban@example.com"
```

### Bước 2: Luôn làm việc trên branch riêng
```powershell
# Cập nhật main trước
git checkout main
git pull origin main

# Tạo branch cá nhân theo format
git switch -c contrib/<github_username>
```

### Bước 3: Commit và tạo Pull Request
```powershell
git status
git add <cac_file_minh_phu_trach>
git commit -m "feat(scope): mô tả rõ phần việc đã làm"
git push -u origin contrib/<github_username>
```

### Bước 4: Nguyên tắc Merge của Trưởng nhóm
> [!CAUTION]
> **TUYỆT ĐỐI KHÔNG DÙNG SQUASH MERGE**!
> Nếu dùng Squash Merge, GitHub sẽ gộp tất cả commit của thành viên thành 1 commit duy nhất đứng tên Trưởng nhóm. Điều này khiến thành viên bị mất bằng chứng commit và bị coi là không tham gia làm bài.
> 👉 **Chỉ dùng: "Create a merge commit" hoặc "Rebase and merge"**.

### Bước 5: Lệnh kiểm tra danh tính trước khi nộp
Chạy lệnh sau trên nhánh nộp bài cuối cùng:
```powershell
git log --format="%h | %an <%ae> | %s"
```
👉 **Điều kiện cần**: Bắt buộc phải nhìn thấy tên và ít nhất 1 commit của cả 5 thành viên xuất hiện trong danh sách.

---

## 5. Checklist an toàn trước khi nộp bài

- [ ] File `TEAMMATES.md` tại thư mục gốc có đủ 5 thành viên (Họ tên, MSSV, GitHub username, Vai trò).
- [ ] Mỗi thành viên trong 5 người đều có ít nhất 1 commit riêng trong Git log.
- [ ] File `version_log.csv` ghi đủ 4 phiên bản: `v0`, `v1`, `v2`, `v3`.
- [ ] File `eval_group.json` có đúng 10 cases (5 single-turn + 5 multi-turn).
- [ ] Giao diện `app.py` chạy mượt mà, hiển thị rõ tool calls, args, results, errors.
- [ ] File `REPORT.md` đã điền đủ Phần A, B, C1 và đủ 5 bản self-reflection C2 của 5 người.
- [ ] **Vệ sinh bảo mật**: Không có file `.env`, API key, thư mục `.venv/`, cache Python hoặc các file json trong `tickets/`.
- [ ] **Nộp bài VLearn**: Cả 5 thành viên dùng tài khoản cá nhân nộp **cùng một đường link GitHub chung** của nhóm (`https://github.com/tungne1311/K4A-Day04-5AESIUNHAN`).
