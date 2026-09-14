# TEAMMATES

Thông tin các thành viên của nhóm nộp bài Lab Day 04.

| STT | Họ và tên đầy đủ | MSSV | GitHub username | Vai trò |
|---:|---|---|---|---|
| 1 | Nguyễn Sơn Giang | 2A202602747 | songiangvn | Nhóm trưởng + Prompt Architect |
| 2 | Nguyễn Đình Phúc | 2A202602953 | rin1652 | Tool & Schema Engineer |
| 3 | Nguyễn Ngọc Thái An | 2A202602462 | nnthaian | Eval & Red-Team |
| 4 | Lê Tuấn Anh | 2A202602952 | anhltsefpt | UI & Report Lead |
| 5 | Vũ Thường Tín | 2A202602955 | Nituv05 | Security & Bonus Tool |

## Vai trò

- **Prompt Architect**: phụ trách `starter_v0/artifacts/system_prompt.md` và
  `version_log.csv`.
- **Tool & Schema Engineer**: phụ trách `starter_v0/artifacts/tools.yaml` và
  tool declarations.
- **Eval & Red-Team**: phụ trách `starter_v0/data/eval_group.json` và
  adversarial evidence.
- **UI & Report Lead**: phụ trách `starter_v0/app.py`, transcript và
  `starter_v0/artifacts/REPORT.md`.
- **Security & Bonus Tool**: phụ trách rà soát data leakage, kiểm tra ticket rác
  và xây tool bonus `approved_software_catalog`.

## Đóng góp trong Git history

Kiểm tra trên branch nộp bài:

```powershell
git log --format="%h | %an <%ae> | %s"
```

| Thành viên | Đóng góp chính | Commit / PR |
|---|---|---|
| Nguyễn Sơn Giang | Baseline v0, failure analysis, `system_prompt.md` v2–v5, guardrail lớp hai trong `create_ticket`, đo metric và ghi version log | `bb1856a`, `e0c47ef`, `98668d2`, `56fae43`, `615a121`, `35c35c7`, `7462f02`, `2396005`, `3ca6d85`, `7a44f6e` |
| Nguyễn Đình Phúc | `tools.yaml` v1 — ranh giới capability và argument semantics | `fcac9dd` (PR #1) |
| Nguyễn Ngọc Thái An | 10 case `eval_group.json` (G01–G10) | `4fe72e6` (PR #2) |
| Lê Tuấn Anh | Live Chat UI Streamlit (`app.py`) | `974c944` (PR #4) |
| Vũ Thường Tín | Cập nhật UI; bonus tool `approved_software_catalog` và security smoke script | `acf9641` (PR #4), `8123c30` (PR #5) |

Mọi thành viên đều có ít nhất một commit dưới Git identity của mình trên branch
nộp bài, theo yêu cầu của `SUBMISSION-GUIDE.md`. Các pull request được merge
bằng `--no-ff`, không squash, để giữ nguyên commit riêng của từng người.
