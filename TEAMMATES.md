# Teammates — K4-DAY04-2A202602531

| # | Họ và tên | MSSV | GitHub | Vai trò |
|---|---|---|---|---|
| 1 | Đỗ Ngọc Phi | 2A202602531 | [@phido0410](https://github.com/phido0410) | A — Prompt Architect / Lead (nhóm trưởng) |
| 2 | Phạm Cường Quốc | 2A202602469 | [@pcq3014](https://github.com/pcq3014) | B — Tool & Schema Engineer |
| 3 | Đỗ Đức Đại | 2A202602725 | [@DucDai1704](https://github.com/DucDai1704) | C — Eval & Red-Team |
| 4 | Nguyễn Trường Bảo | 2A202602540 | [@zewolkt3939](https://github.com/zewolkt3939) | D — UI & Report Coordinator |

## Phạm vi phụ trách

- **A — Prompt Architect / Lead:** `starter_v0/artifacts/system_prompt.md`, format JSON đầu ra,
  context carry-over, version hash và `starter_v0/artifacts/version_log.csv`; chạy các run
  chính thức v0–v3; review và merge pull request.
- **B — Tool & Schema Engineer:** `starter_v0/artifacts/tools.yaml`, chuẩn hóa enum/arguments,
  đồng bộ tool name với registry, Tavily API.
- **C — Eval & Red-Team:** `starter_v0/data/eval_group.json` (10 case: 5 single-turn + 5
  multi-turn), chạy và review 12 adversarial cases.
- **D — UI & Report Coordinator:** Live Chat UI (dùng lại `run_model_tool_loop`), kịch bản demo,
  tổng hợp `starter_v0/artifacts/REPORT.md`.

## Quy trình đóng góp

- Mỗi thành viên làm trên branch `contrib/<github_username>` và mở pull request vào `main`.
- Nhóm trưởng review và merge, không dùng squash merge để giữ commit của từng thành viên.
- Không commit `.env`, API key, `.venv`, cache hoặc generated tickets.
