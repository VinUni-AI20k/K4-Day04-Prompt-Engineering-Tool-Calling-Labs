# Danh Sách Thành Viên & Phân Công Nhiệm Vụ — Day 04 Lab

**Tên Nhóm / Repository:** `K4-Day04-02560-TaVietCuong`  
**Bài Lab:** Day 04 — IT Helpdesk Agent (Prompt Engineering & Tool Calling)

---

## 1. Danh sách thành viên

| STT | Họ và Tên | MSSV | GitHub Username | Vai trò chính |
|:---:|---|:---:|---|---|
| 1 | **Tạ Việt Cường** | 02560 | `ratrichero` | **Prompt Architect / Team Lead** |
| 2 | **Chung Văn Duy** | 02854 | `[github_username_duy]` | **Tool & Schema Engineer** |
| 3 | **Dương Đạt Khang** | 02624 | `[github_username_khang]` | **Eval & Red-Team Specialist** |
| 4 | **Trần Trọng  Chinh** | 02720 | `Chinhdz108` | **UI & Report Coordinator** |

---

## 2. Chi tiết vai trò và trách nhiệm đề xuất

### 1. Tạ Việt Cường — Prompt Architect & Team Lead
* **Quản lý Artifact:** `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/version_log.csv`.
* **Nhiệm vụ chính:**
  * Chủ trì xây dựng và tối ưu `system_prompt.md` qua các phiên bản `v0` $\rightarrow$ `v3`.
  * Chuẩn hóa cấu trúc JSON đầu ra (`intent`, `action`, `reply`, `evidence_ids`).
  * Xử lý context carry-over, quy tắc nhận diện intent, tránh tự suy diễn identifier (`asset_id`, `employee_id`).
  * Điều phối quá trình chạy eval, ghi nhận hypothesis và quản lý hash phiên bản artifact.

### 2. Chung Văn Duy — Tool & Schema Engineer
* **Quản lý Artifact:** `starter_v0/artifacts/tools.yaml`, `starter_v0/tools/`.
* **Nhiệm vụ chính:**
  * Quản lý, chuẩn hóa khai báo mô tả và schema trong `tools.yaml` (descriptions, parameters, enums, required fields).
  * Đảm bảo tính đồng bộ 100% giữa schema khai báo và triển khai code trong Python (`tools/__init__.py`).
  * Quản lý ranh giới dữ liệu và tích hợp API tìm kiếm ngoài Tavily (`search_device_info`), ngăn chặn rò rỉ thông tin nội bộ ra web.
  * Hỗ trợ xây dựng hoặc kiểm thử Tool Bonus (nếu nhóm thực hiện).

### 3. Dương Đạt Khang — Eval & Red-Team Specialist
* **Quản lý Artifact:** `starter_v0/data/eval_group.json`, `starter_v0/data/eval_adversarial.json`, `starter_v0/data/eval_base.json`.
* **Nhiệm vụ chính:**
  * Tác giả chính của bộ test đánh giá riêng của nhóm trong `eval_group.json` gồm đúng 10 test case nguyên bản (G01 $\rightarrow$ G10: 5 single-turn + 5 multi-turn).
  * Thực thi và phân tích chuyên sâu 12 kịch bản tấn công trong `eval_adversarial.json` (prompt injection, state spoofing, bypass xác nhận, trích xuất dữ liệu nhạy cảm).
  * Đối soát trace logs, phát hiện các trường hợp regression hoặc tool lỗi ngầm để báo lại nhóm điều chỉnh prompt/schema.

### 4. Trần Trọng Chinh — UI & Report Coordinator
* **Quản lý Artifact:** `starter_v0/chat.py` (hoặc Streamlit UI), `starter_v0/artifacts/REPORT.md`, `starter_v0/transcripts/`.
* **Nhiệm vụ chính:**
  * Xây dựng và vận hành giao diện Live Chat tương tác (Streamlit / CLI / Web UI), trực quan hóa rõ ràng: Tool calls, args, kết quả thực thi và phiên bản artifact.
  * Chuẩn bị và diễn tập (rehearse) 3–5 kịch bản demo trực quan cho buổi báo cáo.
  * Tổng hợp số liệu thực nghiệm, trace logs và điều phối hoàn thiện báo cáo cuối kỳ `artifacts/REPORT.md` (bao gồm reflection chung và đôn đốc self-reflection của các thành viên).

---

## 3. Quy ước Git & Phối hợp làm việc
* **Nhánh chính (Production / Nộp bài):** Nhánh `main`. Toàn bộ sản phẩm cuối cùng nộp trên VLearn sẽ nằm trên nhánh này.
* **Nhánh làm việc của từng thành viên:** 
  * Mỗi thành viên tự tạo và làm việc trên nhánh riêng của mình (ví dụ: `cuongtv`, `contrib/<github_username>`).
  * Thành viên tự commit công việc dưới Git identity cá nhân của mình:
    ```powershell
    git checkout -b contrib/<github_username>
    git add <cac_file_thay_doi>
    git commit -m "feat(scope): mo ta dong gop"
    git push -u origin contrib/<github_username>
    ```
* **Quy trình Review & Merge:**
  * Sau khi hoàn thành phần việc, thành viên tạo Pull Request (PR) từ nhánh cá nhân vào nhánh `main`.
  * **Nhóm trưởng (Lead)** chịu trách nhiệm kiểm tra (review code, đối soát artifact, đảm bảo không có lỗi hay secret/cache bị lọt vào) rồi mới tiến hành merge vào nhánh `main`.
  * **Lưu ý:** Không sử dụng *Squash merge* khi merge PR nhằm bảo toàn lịch sử commit riêng biệt của từng thành viên trên nhánh `main`.
* **Yêu cầu nộp bài:**
  * Lịch sử `git log` trên nhánh `main` bắt buộc phải có **ít nhất 1 commit cá nhân** tương ứng với từng thành viên trong danh sách `TEAMMATES.md`.
  * Tuyệt đối **không commit** file cấu hình `.env`, API key cá nhân, thư mục `.venv`, cache hoặc dữ liệu giả lập tự sinh trong quá trình chạy test.
