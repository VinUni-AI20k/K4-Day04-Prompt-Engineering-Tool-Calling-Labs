# TEAMMATES — Day 04 Lab (IT Helpdesk Agent)

Repository nộp bài (fork chung của nhóm): https://github.com/vuhuyng04/K4-Day04-2A202602662
Repository nguồn: https://github.com/VinUni-AI20k/K4-Day04-Prompt-Engineering-Tool-Calling-Labs

## Thành viên

| # | Họ tên | MSSV | GitHub username | Vai trò |
|---|---|---|---|---|
| 1 | Nguyễn Vũ Huy | 2A202602662 | vuhuyng04 | Nhóm trưởng. Setup + baseline v0, ba vòng cải tiến v1–v3 (`system_prompt.md`, `tools.yaml`, `version_log.csv`), UI chat, tổng hợp `REPORT.md`, review/merge PR. |
| 2 | _TODO — tự điền_ | _TODO_ | thiendao | Team eval: viết đúng 10 case original trong `starter_v0/data/eval_group.json` (5 single-turn + 5 multi-turn), điền bảng B3 trong `REPORT.md`. |
| 3 | _TODO — tự điền_ | _TODO_ | _TODO_ | Adversarial review: đọc run JSON suite adversarial (v0 và v3), review thủ công ≥3 security case, điền bảng B4a + B6 trong `REPORT.md`. |

Mỗi thành viên tự sửa dòng của mình trong bảng trên và commit bằng Git identity của chính mình.

## Quy trình cộng tác

1. Mỗi người làm trên nhánh riêng `contrib/<github_username>` tách từ `main`.
2. Hoàn thành phần việc → `git add` các file đã đổi → commit bằng Git identity của mình
   (`git config user.name` / `git config user.email` phải khớp tài khoản GitHub).
3. `git push -u origin contrib/<github_username>` rồi mở Pull Request vào `main`.
4. Nhóm trưởng review và merge bằng **merge commit** (không squash) để giữ commit của từng người.
5. Mỗi thành viên phải có **ít nhất một commit kỹ thuật** (không chỉ reflection) trên `main` trước khi nộp.
6. Mỗi thành viên tự viết và tự commit mục C2 (self-reflection) của mình trong `starter_v0/artifacts/REPORT.md`.

## Phần việc không cần API key

- `thiendao`: `eval_group.json` là JSON thuần, theo schema `starter_v0/samples/eval_group.schema.example.json`.
  Nhóm trưởng sẽ chạy suite `group` và gửi lại kết quả.
- Thành viên 3: dùng file run trong `starter_v0/runs/` (do nhóm trưởng push) để phân tích
  `tool_results`, kiểm tra `tickets/` và body gửi ra external search.

## Không commit

`.env`, API key/token, `.venv`, `__pycache__`, `starter_v0/tickets/` (generated ticket), dữ liệu thật.
