# Prompt cho D — UI & Report Coordinator (HieuLM7714)

> Copy toàn bộ phần dưới vào coding agent, mở tại thư mục gốc của repo chung.

---

Bạn là coding agent hỗ trợ tôi (GitHub `HieuLM7714`, vai trò **D — UI & Report Coordinator**) trong bài lab nhóm "Day 04 — IT Helpdesk Agent". Repo: `https://github.com/pbaodev/K4-Day04-2A202602767`. Làm việc trong `starter_v0/`.

## Bối cảnh bắt buộc đọc trước
1. `README.md` (mục "Expectation đầu ra bắt buộc"), `LAB-GUIDE.md` mục 9–10, `TOOL-SETUP.md` mục 10, `docs/team-prompts/README.md`.
2. `starter_v0/chat.py` — đặc biệt `run_model_tool_loop(...)`, `execute_tool_call`, `trim_history`, `write_transcript` và cách `main()` dựng transcript.
3. `starter_v0/versioning.py` (`build_artifact_version`), `starter_v0/providers/__init__.py` (`make_provider`), `starter_v0/tools/__init__.py`.
4. `starter_v0/samples/transcripts/example_helpdesk.transcript.json` (format mẫu).
5. `starter_v0/artifacts/REPORT.md` (template), `artifacts/version_log.csv`, `runs/`.

## Setup
```bash
git pull origin main
git switch -c contrib/HieuLM7714
cd starter_v0
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt "streamlit>=1.30.0"
test -f .env || cp .env.example .env
```
Tôi tự điền `GROQ_API_KEY=...`, `GROQ_MODEL=qwen/qwen3.8-27b` (key free tại https://console.groq.com/keys). Agent không đọc/in/commit giá trị key.

## Nhiệm vụ

### 1. `starter_v0/app.py` — Streamlit live chat
Yêu cầu cứng:
- **Tái sử dụng `run_model_tool_loop` từ `chat.py`** — không viết agent loop mới, không gọi provider trực tiếp.
- Sidebar: chọn provider (mặc định `groq`), model (mặc định lấy `provider.default_model`), version label (text, ví dụ `v3`), `history_window`, `max_tool_rounds`; hiển thị `artifact_version`, `prompt_hash`, `tools_hash` (dùng `build_artifact_version`), nút "New conversation".
- Mỗi turn hiển thị: user message, final assistant text, `status` (answered / waiting_for_user / max_tool_rounds / provider_error), và với **từng round**: tool name, args (JSON), result hoặc error (JSON, có expander). Tool result có `error` phải được highlight (ví dụ `st.error`).
- Nếu assistant text là JSON có `reply` thì render `reply` nổi bật, vẫn cho xem JSON gốc.
- Ghi transcript **cùng format với `chat.py`** vào `transcripts/<version>_<provider>_<timestamp>.transcript.json` sau mỗi turn (tái sử dụng `write_transcript`), hiển thị path.
- Lịch sử hội thoại: `trim_history(history, window)` giống CLI.
- Bắt exception provider → hiển thị lỗi, ghi `status: provider_error` vào transcript, không crash app.
- Không hiển thị/log API key.
- Thêm `streamlit>=1.30.0` vào `requirements.txt`.
- Chạy: `streamlit run app.py`. Kiểm tra app khởi động và một turn chạy được.

### 2. Transcript evidence (sau khi lead merge v3)
Dùng UI (hoặc `python chat.py --provider groq --version v3`) ghi **ít nhất 4 transcript**, mỗi cái một scenario:
1. Normal: một yêu cầu 1 tool (ví dụ trạng thái dịch vụ).
2. Missing-info: thiếu asset/employee ID → agent gọi `clarify`, user bổ sung ở turn sau → agent gọi đúng tool.
3. Multi-turn: correction hoặc cancellation qua ≥ 3 turn.
4. Action boundary: yêu cầu tạo ticket → agent xin xác nhận yes/no → user đổi payload → agent xin xác nhận lại → user xác nhận → ticket được tạo đúng payload cuối.
Chụp screenshot UI cho mỗi scenario (lưu `docs/screenshots/`, **che key/đường dẫn nhạy cảm nếu có**). Xoá `tickets/*.json` sau khi ghi evidence.

### 3. Demo rehearsal
Chọn 3–5 scenario, mỗi cái có câu chuyện: v0 sai gì → hypothesis → artifact đổi → trace thay đổi → giới hạn còn lại. Dùng run JSON trong `runs/` làm fallback nếu mạng/provider lỗi. Ghi vào REPORT mục A4.

### 4. Tổng hợp `artifacts/REPORT.md`
- Điền PHẦN A (A1–A4) và PHẦN B (B1–B7) dựa trên evidence thật trong repo: `version_log.csv`, `runs/*.json`, `transcripts/`, PR của B (tools v2), C (group + adversarial), E (security + bonus).
- Mọi con số phải trích từ run JSON (`summary`), kèm path run file. Ghi rõ provider/model: `groq / qwen/qwen3.8-27b`.
- Có thể dùng `python scripts/parse_runs.py --help` để xuất bảng phân tích.
- PHẦN C1 (reflection chung): soạn **bản nháp** dựa trên evidence để cả nhóm thảo luận/chỉnh.
- PHẦN C2 (self-reflection từng người): **làm sớm nhất có thể một PR nhỏ** chỉ tạo sẵn 5 block (một block/thành viên theo thứ tự `TEAMMATES.md`, mỗi block cách nhau bằng dòng `---`), để trống nội dung. Mỗi thành viên sau đó chỉ sửa block của mình → tránh conflict khi nhiều PR cùng sửa `REPORT.md`.

### 5. Commit & PR
- Commit: `app.py`, `requirements.txt`, `transcripts/*.transcript.json` (v3), `docs/screenshots/`, `artifacts/REPORT.md`.
- Commit bằng Git identity của tôi, ví dụ `feat(ui): streamlit live chat reusing run_model_tool_loop`, `docs(report): compile evidence`.
- Push `contrib/HieuLM7714`, mở PR vào `main`.

## Ràng buộc
- Không sửa `system_prompt.md`, `tools.yaml`, eval datasets.
- Không commit `.env`, key, `.venv`, `tickets/`.
- Không bịa số liệu trong report — nếu evidence chưa có, để `TODO(<người phụ trách>)`.
- Không viết self-reflection thay người khác.

## Definition of done
- [ ] `streamlit run app.py` chạy, hiển thị tool calls/args/result/error/status/artifact version, dùng `run_model_tool_loop`.
- [ ] ≥ 4 transcript v3 đủ 4 loại scenario + screenshot.
- [ ] REPORT A + B điền đầy đủ từ evidence, C1 có bản nháp.
- [ ] PR mở vào `main` với commit của `HieuLM7714`.
