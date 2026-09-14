# Quy ước làm việc nhóm — Lab Day 04

Tài liệu nội bộ của nhóm. Yêu cầu chính thức nằm ở `README.md`,
`LAB-GUIDE.md` và `SUBMISSION-GUIDE.md`.

## 1. Provider và model

Cả nhóm dùng **một** provider và **một** model cho toàn bộ v0 → v3:

```text
provider: openai
model:    gpt-4o-mini   (mặc định của provider, không truyền --model)
```

Lý do: metric chỉ so sánh được khi provider/model không đổi. Nếu v1 chạy model
khác v0 thì chênh lệch metric không chứng minh được prompt đã tốt hơn.

Mỗi người tự tạo `starter_v0/.env` từ `.env.example`. Không commit `.env`,
không dán key vào chat, issue hay PR.

## 2. Ai sở hữu file nào

Chỉ sửa file thuộc phần việc của mình. Muốn sửa file của người khác thì báo
trong PR thay vì sửa thẳng.

| Role | File sở hữu |
|---|---|
| A — Prompt Architect / Lead | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/version_log.csv` |
| B — Tool & Schema | `starter_v0/artifacts/tools.yaml` |
| C — Eval & Red-team | `starter_v0/data/eval_group.json` |
| D — UI & Report | `starter_v0/app.py`, `starter_v0/artifacts/REPORT.md` |
| E — Security & Bonus tool | `starter_v0/tools/<tool_moi>/`, `starter_v0/tools/__init__.py` |

File dùng chung, phải báo trước khi sửa:

- `starter_v0/tools/__init__.py` — B và E cùng đụng khi thêm/đổi tool;
- `starter_v0/requirements.txt` — D thêm streamlit, E có thể thêm dependency;
- `starter_v0/artifacts/REPORT.md` — mục C2 mỗi người tự commit phần của mình.

## 3. Không đổi tên tool

Giữ nguyên 9 tên tool hiện có. `data/eval_base.json` hard-code tên tool trong
30 case và ghi rõ không được sửa expected behavior; đổi tên sẽ làm eval báo
"not declared in tools.yaml" hoặc chấm sai toàn bộ.

B được sửa `description`, `parameters`, `enum`, `required` — không sửa `name`.

Tool bonus của E là tên mới, không ảnh hưởng eval có sẵn, nhưng phải đồng bộ:
`tools.yaml` -> `tools/__init__.py` -> `tools/<name>/TOOL.md` -> eval case của nhóm.

## 4. Thứ tự làm việc

Lab này không song song hoàn toàn được: version log yêu cầu mỗi version sửa
**một** artifact với **một** hypothesis, rồi chạy lại để so metric.

| Giai đoạn | Ai | Nội dung |
|---|---|---|
| 0. Nền | A | venv, smoke test, preflight, quy ước |
| 1. Baseline v0 | A | Chạy base suite với artifact nguyên bản, chưa sửa gì |
| 2. Song song | B, C, D, E | C viết eval; D dựng UI; E làm bonus tool; B phân tích run v0 |
| 3. v1 → v3 | A và B luân phiên | v1 prompt, v2 tools.yaml, v3 prompt — chạy eval sau MỖI version |
| 4. Evidence | cả nhóm | group/extension/adversarial trên v3, report, self-reflection |

Không ai sửa `system_prompt.md` hoặc `tools.yaml` trước khi v0 chạy xong.

## 5. Branch và commit

```powershell
git switch -c contrib/<GITHUB_USERNAME>
# ...lam phan viec cua minh...
git status
git add <file_da_thay_doi>
git commit -m "feat(scope): mo ta dong gop"
git push -u origin contrib/<GITHUB_USERNAME>
```

Kiểm tra Git identity trước commit đầu tiên — commit sai identity sẽ không được
tính là đóng góp:

```powershell
git config user.name
git config user.email
```

Mỗi thành viên phải có **ít nhất một commit** xuất hiện trên branch nộp bài.

## 6. Merge (lead làm)

Không squash. Squash gộp commit của thành viên vào một commit mang tên lead,
làm mất bằng chứng đóng góp.

```powershell
git switch main
git merge --no-ff contrib/<GITHUB_USERNAME>
cd starter_v0; python -m compileall -q .
```

Thứ tự merge ưu tiên file ít va chạm trước: C -> E -> D -> B.
Sau khi merge PR của B (`tools.yaml`), phải chạy lại eval trước khi sang version
tiếp theo.

Kiểm tra đủ mặt thành viên trước khi nộp:

```powershell
git log --format="%h | %an <%ae> | %s"
```

## 7. Evidence

`starter_v0/runs/` và `starter_v0/transcripts/` bị gitignore. Bản sao đã review
được đặt trong `starter_v0/evidence/` — xem `starter_v0/evidence/README.md`.

Một run chỉ dùng làm evidence khi:

```text
provider_error_cases == 0
measured_cases == total_cases
```

Tool result có error hoặc empty vẫn phải review thủ công, kể cả khi evaluator
chấm PASS.

## 8. Không commit

`.env`, API key, token, `.venv/`, `__pycache__/`, generated ticket trong
`tickets/`, dữ liệu thật.
