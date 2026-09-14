# Prompt cho E — Security & Bonus Tool (DuyBach2003)

> Copy toàn bộ phần dưới vào coding agent, mở tại thư mục gốc của repo chung.

---

Bạn là coding agent hỗ trợ tôi (GitHub `DuyBach2003`, vai trò **E — Security & Bonus Tool**) trong bài lab nhóm "Day 04 — IT Helpdesk Agent". Repo: `https://github.com/pbaodev/K4-Day04-2A202602767`. Làm việc trong `starter_v0/`.

## Bối cảnh bắt buộc đọc trước
1. `README.md` (mục "Ranh giới an toàn", "Tool mới của nhóm — Bonus"), `LAB-GUIDE.md` mục 8 và 11, `TOOL-SETUP.md` mục 6–7 và 12, `docs/team-prompts/README.md`.
2. Implementation: `starter_v0/tools/_shared.py`, `tools/create_ticket/`, `tools/search_device_info/`, `tools/search_kb/`, `tools/policy/`, `tools/__init__.py`.
3. `starter_v0/data/eval_adversarial.json` và run adversarial trong `starter_v0/runs/` (v0 đã có evidence: A04 tạo ticket critical từ payload user dán vào; A12 gọi `search_device_info` với model chứa `LT-204 EMP-1001`).
4. `starter_v0/artifacts/tools.yaml`, `artifacts/system_prompt.md` (không sửa — thuộc B và A).

## Setup
```bash
git pull origin main
git switch -c contrib/DuyBach2003
cd starter_v0
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
```
Tôi tự điền `GROQ_API_KEY=...`, `GROQ_MODEL=qwen/qwen3.8-27b`, và (nếu test Tavily) `TAVILY_API_KEY=...`. Agent không đọc/in/commit giá trị key.

## Nhiệm vụ

### 1. Security review — lớp implementation (defense in depth)
Mục tiêu: kể cả khi model gọi sai, tool vẫn từ chối input nguy hiểm. Viết **deterministic test** (không gọi model) cho từng điểm, ví dụ `starter_v0/tests/test_security_guards.py`. Ưu tiên chỉ dùng thư viện chuẩn (`unittest`, chạy `python -m unittest discover tests`) để khỏi sửa `requirements.txt` (file của D):
- `create_ticket`:
  - `confirmed` phải là Boolean `True` thật: `"true"`, `1`, `{}`, `None` → `needs_confirmation`, **không tạo file**.
  - `summary`/`asset_id` chứa password, token, API key, MFA/OTP, recovery code (ví dụ `password=...`, `otp 123456`, `sk-...`, `tvly-...`) → bị từ chối, không tạo file.
  - Test ghi file phải dùng thư mục tạm (monkeypatch đường dẫn tickets), không làm bẩn `starter_v0/tickets/`.
- `search_device_info`:
  - `manufacturer`/`model` chứa asset ID (`LT-204`, `DT-031`), employee ID (`EMP-1001`), serial, hostname, location, email → bị chặn **trước khi gửi request** (mock `requests.post`/network, assert không được gọi).
  - Kiểm tra request body chỉ chứa query công khai; kết quả web có instruction-like text bị lọc.
- `search_kb` / `policy`: instruction-like content (ví dụ file `knowledge_base/printer-injection-probe.md`) nằm trong `untrusted_text`, không lọt vào trusted `content`.
- Unknown tool: `chat.py`/`agent.py` trả `unknown_tool`, không thực thi.

Nếu phát hiện guard **thiếu hoặc lỗi** → sửa implementation tối thiểu trong đúng tool, kèm test. Không dùng prompt để che lỗi implementation. Ghi lại mỗi lỗ hổng tìm được.

### 2. Rà soát evidence run
- Với mọi run trong `runs/` (đặc biệt adversarial v0/v1 và extension): liệt kê mọi `create_ticket` được gọi (args, `confirmed`, result có `ticket_id` không) và mọi `search_device_info` (args có identifier nội bộ không, result error/blocked?).
- Kiểm tra `starter_v0/tickets/`: mỗi file ticket truy ngược về run/case nào; ticket nào tạo khi **chưa có xác nhận hợp lệ** → ghi thành finding.
- Grep toàn repo (trừ `.venv`) xem có key/token/password thật bị commit không: `git grep -nIE "(sk-|gsk_|tvly-|api[_-]?key\s*=\s*\S+|password=)" -- . ':!*.venv*'`.
- Ghi kết quả vào `docs/security-review.md`: bảng `Finding | Evidence (run/case/file) | Impact | Fix (prompt / tools.yaml / implementation) | Test`.
- Sau khi ghi nhận, xoá `tickets/*.json`.

### 3. Bonus tool (một capability mới có ý nghĩa)
Chọn **một**: `ticket_status` (tra trạng thái ticket local theo `ticket_id`, read-only), `software_catalog` (danh sách phần mềm được phê duyệt), `network_diagnostics` (mock ping/DNS cho asset), `meeting_room_inventory`. Khuyến nghị `ticket_status` hoặc `software_catalog` vì read-only, dễ kiểm soát.
Bonus chỉ được tính khi có **đủ**:
- [ ] `tools/<tool_name>/TOOL.md` (input/output contract, data source, error behavior, side effect, privacy boundary, smoke test).
- [ ] `tools/<tool_name>/__init__.py` + `tool.py` chạy được, validate input (ID format), không lộ dữ liệu nhạy cảm.
- [ ] Đăng ký trong `tools/__init__.py` (`TOOL_FUNCTIONS`).
- [ ] Declaration trong `artifacts/tools.yaml` — **không tự sửa file này**: gửi đoạn YAML cho B (buide03) để B đưa vào. **Tool phải merge trước khi A làm v3**; nếu trễ mốc đó thì bonus tool không được đưa vào artifact cuối (tránh làm lệch `tools_hash` của evidence v3).
- [ ] Mock data trong `helpdesk_data/` (dữ liệu giả lập).
- [ ] Smoke test command (thêm vào TOOL.md) + deterministic test.
- [ ] 1 team eval case — **gửi C (keilelser-05)** đưa vào `eval_group.json`.
- [ ] Evidence UI/transcript (phối hợp D) và mục B5 trong report.
- [ ] Guardrail tương ứng side effect/dữ liệu.
Đổi tên tool cũ hoặc folder rỗng không được tính.

### 4. Commit & PR
- Tách commit theo nội dung, bằng Git identity của tôi, ví dụ:
  - `test(security): deterministic guards for create_ticket and search_device_info`
  - `fix(tools): block <...> in <tool>` (nếu có)
  - `feat(tools): add <bonus_tool> with mock data and smoke test`
  - `docs(security): security review findings`
- Push `DoanDuyBach_2A202602515`, mở PR vào `main`, mô tả findings + test output.

### 5. Góp nội dung REPORT (gửi D tổng hợp)
- B5 (optional/bonus evidence), B6 (safety review — trả lời 4 câu hỏi bằng evidence), dòng security trong B7.

## Ràng buộc
- Không sửa eval datasets cố định, không sửa `system_prompt.md`.
- Không gọi Tavily thật trong unit test (mock network). Chỉ smoke test Tavily khi có key.
- Không commit `.env`, key, `.venv`, `tickets/`, dữ liệu thật.
- Không tự viết self-reflection C2 — tôi tự viết.
- Nếu một fix cần đổi behavior mà eval đang dựa vào, dừng lại và hỏi tôi.

## Definition of done
- [x] Test security deterministic pass; mọi lỗ hổng tìm được có fix + test hoặc được ghi rõ là giới hạn.
- [x] `docs/security-review.md` có findings truy ngược tới run/case/file.
- [ ] (Bonus) tool mới đủ checklist ở mục 3.
- [x] `tickets/` sạch; không có secret trong repo.
- [x] PR mở vào `main` với commit của `DuyBach2003`.
