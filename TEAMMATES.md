# TEAMMATES — Day 04 Lab (IT Helpdesk Agent)

Repository nộp bài (fork chung của nhóm): https://github.com/vuhuyng04/K4-Day04-2A202602662
Repository nguồn: https://github.com/VinUni-AI20k/K4-Day04-Prompt-Engineering-Tool-Calling-Labs

## Thành viên và phân công

| # | Họ tên | MSSV | GitHub username | Vai trò / phần việc |
|---|---|---|---|---|
| 1 | Nguyễn Vũ Huy | 2A202602662 | vuhuyng04 | **Nhóm trưởng — prompt/tool loop.** Setup môi trường, baseline v0, ba vòng cải tiến v1–v3 (`artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, run JSON trong `runs/`), failure analysis (`artifacts/analysis_notes.md`). Review/merge PR, tổng hợp `REPORT.md` phần B1, B2, B7, C1, C3. |
| 2 | _TODO — tự điền_ | _TODO_ | thiendao | **Team eval.** Viết đúng 10 case original trong `starter_v0/data/eval_group.json` (5 single-turn + 5 multi-turn) theo `samples/eval_group.schema.example.json`; mỗi case cô lập một quyết định (ambiguous intent, thiếu ID, correction, cancellation, stale confirmation, format-only, external/internal boundary…). Điền `REPORT.md` B3 sau khi nhóm trưởng chạy suite `group`. |
| 3 | Đỗ Thái Sơn | 2A202603021 | tsun165 | **Adversarial + safety review.** Đọc run JSON suite adversarial (v0 và v3) trong `runs/`, review thủ công ≥3 security case: tool nào thực sự được gọi, `tickets/` có file mới không, body gửi ra `search_device_info` chứa gì, fake SYSTEM/tool-result có đổi hành vi không. Điền `REPORT.md` B4a và B6. Chạy/đọc suite extension (policy, create_ticket, search_device_info) và điền B5 nếu có. |
| 4 | _TODO — tự điền_ | _TODO_ | _TODO_ | **UI chat + live evidence.** Xây `starter_v0/ui.py` (Streamlit/Gradio) tái dùng `run_model_tool_loop` trong `chat.py`, hiển thị user request, final response, từng tool name + args, tool result/error, round/status, artifact version + hashes, transcript path; ghi transcript vào `transcripts/`. Rehearse 3–5 scenario (normal, missing-info, multi-turn correction, ticket confirmation) và điền `REPORT.md` A1–A4, B4. |

Mỗi thành viên tự sửa dòng của mình trong bảng trên và commit bằng Git identity của chính mình.
Mỗi người tự viết và tự commit mục **C2 (self-reflection)** của mình trong `starter_v0/artifacts/REPORT.md`.

## Quy trình cộng tác

1. Mỗi người làm trên nhánh riêng `contrib/<github_username>` tách từ `main`.
2. Hoàn thành phần việc → `git add` các file đã đổi → commit bằng Git identity của mình
   (`git config user.name` / `git config user.email` phải khớp tài khoản GitHub).
3. `git push -u origin contrib/<github_username>` rồi mở Pull Request vào `main`.
4. Nhóm trưởng review và merge bằng **merge commit** (không squash) để giữ commit của từng người.
5. Mỗi thành viên phải có **ít nhất một commit kỹ thuật** (không chỉ reflection) trên `main` trước khi nộp.
6. Chỉ sửa file thuộc phần việc của mình để tránh conflict; nếu cần sửa `system_prompt.md`/`tools.yaml`, trao đổi với nhóm trưởng trước vì mỗi thay đổi tạo ra một artifact version mới.

## Ai cần API key

- Không cần key: thành viên 2 (JSON thuần) và thành viên 3 (đọc run JSON nhóm trưởng đã push).
- Cần key để test: thành viên 4 (UI). Dùng key của chính mình trong `starter_v0/.env` (gitignored); nếu không có, nhóm trưởng sẽ chạy rehearsal và push transcript.

## Không commit

`.env`, API key/token, `.venv`, `__pycache__`, `starter_v0/tickets/` (generated ticket), dữ liệu thật.
