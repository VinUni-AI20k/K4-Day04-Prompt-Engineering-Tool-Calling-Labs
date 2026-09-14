# Prompt cho B — Tool & Schema Engineer (buide03)

> Copy toàn bộ phần dưới vào coding agent, mở tại thư mục gốc của repo chung.

---

Bạn là coding agent hỗ trợ tôi (GitHub `buide03`, vai trò **B — Tool & Schema Engineer**) trong bài lab nhóm "Day 04 — IT Helpdesk Agent". Repo: `https://github.com/pbaodev/K4-Day04-2A202602767`. Làm việc trong `starter_v0/`.

## Bối cảnh bắt buộc đọc trước
1. `README.md`, `LAB-GUIDE.md`, `TOOL-SETUP.md`, `docs/team-prompts/README.md`.
2. `starter_v0/artifacts/tools.yaml` (file tôi sở hữu), `starter_v0/artifacts/system_prompt.md` (của lead, **không sửa**).
3. `starter_v0/tools/__init__.py`, mọi `starter_v0/tools/*/TOOL.md` và `tool.py` — để biết implementation thực sự nhận/trả gì.
4. `starter_v0/data/eval_base.json`, `eval_helpdesk_extension.json`, `eval_adversarial.json` — chỉ để hiểu hành vi mong đợi; **không sửa, không copy wording của case vào description, không hard-code case ID**.
5. Run evidence gần nhất trong `starter_v0/runs/` (v0, v1) và `starter_v0/artifacts/version_log.csv`.

## Setup
```bash
git pull origin main
git switch -c contrib/buide03
cd starter_v0
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
```
Trong `.env` tôi tự điền: `GROQ_API_KEY=...`, `GROQ_MODEL=qwen/qwen3.8-27b`, `TAVILY_API_KEY=...` (lấy free tại https://tavily.com). Agent **không được đọc, in hoặc commit giá trị key**.
Kiểm tra: `python -m compileall -q -x '\.venv' . && python scripts/preflight_provider.py --provider groq`.

## Nhiệm vụ

### 1. Version v2 — chỉ sửa `artifacts/tools.yaml`
Điều kiện: lead đã merge v1 vào `main` (kiểm tra `version_log.csv` có dòng `v1`). Không đổi `system_prompt.md` trong version này để metric chỉ phản ánh thay đổi declaration.

Phân tích failure còn lại ở run v1 (base + adversarial), sau đó viết lại description/schema cho từng tool:
- **Mỗi tool**: nó sở hữu loại dữ liệu nào; khi nào dùng; khi nào **không** dùng (chỉ ra tool đúng thay thế); side effect; ranh giới dữ liệu.
- `check_service_status` (shared service) vs `inspect_device` (một asset cụ thể) vs `lookup_user` (employee record).
- `clarify`: khi nào `text` (thiếu identifier), `yes_no` (xác nhận action ghi), `choice` + `options` (giá trị ngoài enum hợp lệ, ví dụ môi trường không phải production/staging). `question` nên required.
- `inspect_device.check`, `search_kb.category`, `policy.policy_area`: mô tả nghĩa của từng enum value để model chọn đúng.
- `create_ticket`: action ghi; `confirmed` chỉ `true` khi user vừa xác nhận rõ ràng đúng payload hiện tại; không bao giờ đưa password/token/MFA/OTP vào `summary`.
- `format_incident_report`: chỉ format findings đã có, không gọi lại tool thu thập.
- `search_device_info`: chỉ manufacturer + public model + query_type; nếu chuỗi model chứa asset ID/employee ID/serial/hostname thì không gọi mà hỏi lại.
- Identifier format: asset ID dạng `LT-204`/`DT-031`, employee ID dạng `EMP-1003` — không bao giờ tự đoán.
- Nếu E (DuyBach2003) gửi YAML cho bonus tool và tool đó đã merge vào `main`, đưa declaration vào `tools.yaml` trong v2 (hoặc một PR nhỏ riêng trước khi A làm v3). Chỉ mình B sửa `tools.yaml`.
- Giữ nguyên **tên tool** (không rename). Nếu thật sự phải rename, đồng bộ `tools.yaml` → `tools/__init__.py` → `TOOL.md` → eval files, và báo lead trước.

Viết một **hypothesis cụ thể** trước khi chạy, ví dụ: "Nếu description phân biệt rõ khi nào dùng clarify(choice) và mô tả enum, các case missing_info/wrong_arg_value sẽ pass mà không tăng unexpected_tool_call."

### 2. Chạy evidence v2
```bash
python run_eval.py --provider groq --version v2 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider groq --version v2 --suite adversarial --eval-cases data/eval_adversarial.json
```
- Chạy tuần tự (Groq free có giới hạn token/phút; provider đã có auto-retry nên sẽ chậm, cứ để chạy).
- Run chỉ hợp lệ khi `provider_error_cases == 0` và `measured_cases == total_cases`; nếu không, chạy lại.
- Đọc `tool_results` của các case fail/pass đáng ngờ, không chỉ nhìn PASS/FAIL. Nếu so với v1 có case bị regress, ghi rõ.
- Sau khi chạy, xoá file trong `starter_v0/tickets/` (đã ghi nhận vào report nếu cần) — không commit ticket.

### 3. Extension suite + Tavily
```bash
python -c "from pathlib import Path; from env_loader import load_lab_env; load_lab_env(Path.cwd()); from tools import TOOL_FUNCTIONS as T; r=T['search_device_info']('Lenovo','ThinkPad T14 Gen 4','drivers',2); print({'error':r.get('error'),'items':len(r.get('items') or []),'domains':r.get('official_domains')})"
python run_eval.py --provider groq --version v2 --suite extension --eval-cases data/eval_helpdesk_extension.json
```
Ghi nhận domain trả về và bất kỳ tool error nào.

### 4. Ghi version log
Thêm dòng `v2` vào `artifacts/version_log.csv` theo đúng header hiện có: `author=buide03`, `changed_artifact=tools.yaml`, `artifact_version`/`prompt_hash`/`tools_hash` lấy từ run JSON, `metric_name=case_accuracy (base)`, `metric_before` = v1, `metric_after` = v2, `run_file` = path run base v2. Có thể thêm dòng phụ cho adversarial nếu metric chính là adversarial.

### 5. Commit & PR
- Commit các file: `artifacts/tools.yaml`, `artifacts/version_log.csv`, run JSON v2 hợp lệ trong `runs/`.
- Commit message dạng `feat(tools): v2 clarify routing and enum descriptions` — commit bằng Git identity của tôi.
- Push `contrib/buide03`, mở PR vào `main`. Mô tả PR gồm: hypothesis, bảng metric v1→v2 (base, adversarial, extension), 2–3 case thay đổi đáng chú ý, regression nếu có.
- Báo lead (pbaodev) để merge; lead sẽ làm v3 dựa trên v2.

### 6. Góp nội dung cho REPORT (gửi D tổng hợp)
Soạn sẵn (trong PR description hoặc tin nhắn cho D):
- B1 dòng v2; B2 failure do declaration; B5 dòng "External search + privacy boundary" (evidence Tavily); B7 "Fix nào thuộc tools.yaml?".

## Ràng buộc
- Không sửa eval dataset cố định, không sửa `system_prompt.md`, không hard-code case ID/wording.
- Không commit `.env`, key, `.venv`, `tickets/`.
- Không tự viết self-reflection C2 — tôi tự viết.
- Khi không chắc (ví dụ muốn rename tool hoặc sửa implementation), dừng lại và hỏi tôi.

## Definition of done
- [ ] `tools.yaml` v2 load được, tên tool khớp `TOOL_FUNCTIONS`.
- [ ] Run v2 base + adversarial + extension hợp lệ (0 provider error) trong `runs/`.
- [ ] Dòng v2 trong `version_log.csv` có hypothesis + before/after.
- [ ] PR mở vào `main` với commit của `buide03`.
