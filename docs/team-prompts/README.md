# Team agent prompts — Day 04 Lab

Mỗi thành viên mở file của mình, copy **toàn bộ** nội dung vào coding agent
(Claude Code, Codex, Cursor…) đang mở tại bản clone của repo chung.

| Vai trò | GitHub | File |
|---|---|---|
| A — Prompt Architect / Lead | pbaodev | (lead tự làm) |
| B — Tool & Schema Engineer | buide03 | [B-tools-schema.md](B-tools-schema.md) |
| C — Eval & Red-Team | keilelser-05 | [C-eval-redteam.md](C-eval-redteam.md) |
| D — UI & Report Coordinator | HieuLM7714 | [D-ui-report.md](D-ui-report.md) |
| E — Security & Bonus Tool | DuyBach2003 | [E-security-bonus.md](E-security-bonus.md) |

## Thứ tự phụ thuộc

```text
v0 baseline (A, xong) ─> v1 system_prompt (A) ─> v2 tools.yaml (B) ─> v3 system_prompt (A)
                                                                        │
C: viết eval_group.json ngay ───────────────────────────────────────────┤─> chạy group/adversarial trên v3
D: dựng app.py ngay ────────────────────────────────────────────────────┤─> transcript + REPORT trên v3
E: security review + bonus tool ngay ───────────────────────────────────┘
```

## File ownership — tránh xung đột

| File / thư mục | Chủ sở hữu | Người khác |
|---|---|---|
| `artifacts/system_prompt.md`, `providers/`, `.gitignore` | A | không sửa |
| `artifacts/tools.yaml` | B (v2) → A (v3 chỉ đọc) | E gửi YAML bonus tool cho B, **không tự sửa** |
| `artifacts/version_log.csv` | A ghi v0/v1/v3, B ghi v2 | B chỉ append sau khi v1 đã merge |
| `data/eval_group.json`, `docs/adversarial-analysis.md` | C | không sửa |
| `app.py`, `transcripts/`, `docs/screenshots/`, `artifacts/REPORT.md` (A, B, C1) | D | gửi nội dung cho D |
| `REPORT.md` mục C2 — block của từng người | chính người đó | chỉ sửa block của mình |
| `tools/<tool>/tool.py` (guard), `tools/<bonus>/`, `tests/`, `helpdesk_data/<bonus data>`, `docs/security-review.md` | E | không sửa |
| `tools/__init__.py` | E (đăng ký bonus tool) | không sửa |
| `requirements.txt` | D | E nhờ D thêm dependency test nếu cần |

Run evidence chính thức (tránh chạy trùng):

| Version | base | adversarial | extension | group |
|---|---|---|---|---|
| v0, v1 | A | A | — | — |
| v2 | B | B | B | — |
| v3 | A | **C** | B | **C** |

Mốc khoá: **bonus tool (nếu có) phải merge trước khi A làm v3** để `tools_hash` của v3 là bản cuối.
Sau khi v3 được merge, không ai sửa `system_prompt.md` / `tools.yaml` nữa.

Luôn `git pull --rebase origin main` trước khi push và trước khi mở PR; PR nhỏ, merge sớm.

## Quy ước chung (mọi prompt đều nhắc lại)

- Provider/model cố định cho mọi evidence: `--provider groq`, `GROQ_MODEL=qwen/qwen3.8-27b`.
- Mỗi người tự tạo Groq key miễn phí tại https://console.groq.com/keys và điền vào `starter_v0/.env` của mình.
- Branch `contrib/<github-username>`, commit bằng Git identity của chính mình, PR vào `main`, **không squash merge**.
- Không commit `.env`, API key, `.venv`, `tickets/`, cache.
- Không sửa `data/eval_base.json`, `data/eval_helpdesk_extension.json`, `data/eval_adversarial.json`.
- Self-reflection (REPORT.md mục C2) do **chính thành viên** tự viết và tự commit, không để agent viết thay.
