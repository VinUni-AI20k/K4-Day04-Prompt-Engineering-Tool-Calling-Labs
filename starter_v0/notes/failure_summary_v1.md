# Failure summary — v1 (base suite)

Nguoi 1 (Eval/Evidence) ban giao cho Nguoi 2 (prompt) va Nguoi 3 (tools.yaml) de lam v2.

## Run

| Truong | Gia tri |
|---|---|
| Run file | `starter_v0/runs/v1_B_base_openai_20260914T185529502074.json` (local, gitignored) |
| Analysis CSV | `starter_v0/analysis/v1_base_openai_analysis.csv` (local) |
| Provider / model | `openai` / `gpt-4o-mini` (giong v0) |
| Source commit | `19efe0c` (merge prompt `c9bfeb0` + tools `9e946ce`) |
| Artifact version | `v1+p31b50521653e+tb73291e8b8f6` |
| Hop le | `provider_error_cases = 0`, `measured_cases = total_cases = 30` |
| Ticket moi sinh ra | Khong co |

## Metric v0 → v1

| Metric | v0 | v1 |
|---|---:|---:|
| passed_cases | 21 / 30 | **27 / 30** |
| case_accuracy | 0.70 | **0.90** |
| tool_routing_accuracy | 0.7667 | 0.90 |
| argument_accuracy | 0.70 | 0.90 |
| multiturn_accuracy | 0.80 | 0.90 |
| failure_counts | wrong_boundary 3, missing_info 3, wrong_tool 3 | wrong_boundary 2, missing_info 1 |

Thay doi tung case:

- FAIL → PASS (6): H04, H10, H11, H13, H17, M09
- PASS → FAIL (regression): **khong co**

## 3 case con FAIL

| Case | Nhom loi | Expected | Actual v1 | Nhan xet |
|---|---|---|---|---|
| H12_confirm_before_ticket | Confirmation boundary | `clarify(yes_no)` | `create_ticket(..., confirmed=false)` | Da an toan hon v0 (khong ghi ticket), nhung model dung `create_ticket` dry-run thay vi hoi xac nhan bang `clarify` |
| M05_ticket_confirmation (multi-turn) | Confirmation boundary | `clarify(yes_no)` | `create_ticket(priority=high, confirmed=false)` | Cung pattern: goi write tool voi `confirmed=false` de "hoi xac nhan" |
| H19_ambiguous_environment | Missing info (enum) | `clarify(choice, options=[production, staging])` | `check_service_status(email, environment="demo")` | Model truyen gia tri ngoai enum → tool tra `not_found` |

## Nguyen nhan du doan

1. `tools.yaml` mo ta `create_ticket` "returns needs_confirmation when confirmed=false" → model hieu goi `create_ticket(confirmed=false)` la cach hop le de xin xac nhan. Prompt noi "obtain explicit confirmation" nhung khong noi ro **dung tool nao** de xin.
2. OpenAI khong ep enum chat che, nen model van truyen `"demo"`. Mo ta clarify cho environment chi nam trong `check_service_status.environment`; prompt chua co rule chung ve gia tri enum khong ro.

## De xuat cho v2

### Nguoi 2 — `system_prompt.md`

1. **Loi dinh dang can sua truoc**: file dang chua ky tu diff (dong bat dau bang `+` hoac dau cach thua o dau dong, vd `+- Distinguish ...`). Can xoa cac ky tu nay de prompt sach. Luu y: sua xong prompt hash se doi, nen phai chay lai eval.
2. Rule: de xin xac nhan write action, goi `clarify(response_type=yes_no)` voi tom tat payload; **khong** goi `create_ticket` cho den khi user da tra loi dong y. (H12, M05)
3. Rule: gia tri enum (environment, service, priority...) khong khop ro rang voi lua chon hop le → `clarify(response_type=choice)` voi `options` la cac gia tri hop le; khong tu map, khong truyen gia tri ngoai enum. (H19)

Hypothesis goi y: "Neu prompt chi dinh ro `clarify` yes_no la buoc bat buoc truoc `create_ticket` va enum mo ho phai clarify choice, H12/M05/H19 se PASS ma khong gay regression."

### Nguoi 3 — `tools.yaml`

1. `create_ticket`: bo/doi cach viet de khong goi y goi tool voi `confirmed=false` de xin xac nhan; ghi ro "Chua co xac nhan → goi `clarify` yes_no, KHONG goi tool nay". (H12, M05)
2. `clarify`: them vi du `choice` cho environment mo ho, `options: [production, staging]`. (H19)
3. `lookup_user.employee_id`: format dang ghi `EMP-NNN` nhung du lieu that la `EMP-NNNN` (vd `EMP-1003`) — sua lai de tranh model clarify nham.
4. `inspect_device.asset_id`: du lieu con prefix `KK-` va `MP-` chua duoc liet ke trong pattern `LT|DT|MB|PR|RM`.

## Phat hien them sau khi chay lai (tren `main` 104ba19, artifact van la v1)

- **H12 khong on dinh**: chay lai co luc model goi `inspect_device(LT-204, vpn)` thay vi `create_ticket(confirmed=false)`, nhung lan nao cung bo qua `clarify` yes_no. Rule xac nhan can viet ro, khong dua vao may man.
- **Output khong phai JSON**: prompt yeu cau JSON `intent`/`action`/`reply`/`evidence_ids`, nhung khi chat (UI hoac `chat.py`) model tra van ban thuong. Eval base khong cham phan nay, nhung demo/report se thay. (Nguoi 2)
- Khong co ticket moi sinh ra trong v1.

## Lenh kiem tra nhanh cho Nguoi 2 / Nguoi 3

Chay tu `starter_v0`, sau `.\.venv\Scripts\Activate.ps1`. Chi chay 3 case dang FAIL (tiet kiem quota, file run nam trong `analysis/debug_runs`, khong lan voi evidence chinh thuc):

```powershell
python -c "import json; d=json.load(open('data/eval_base.json',encoding='utf-8')); ids={'H12_confirm_before_ticket','M05_ticket_confirmation','H19_ambiguous_environment'}; d['cases']=[c for c in d['cases'] if c['id'] in ids]; json.dump(d,open('analysis/eval_v1_failing.json','w',encoding='utf-8'),ensure_ascii=False,indent=2); print(len(d['cases']),'cases')"
python run_eval.py --provider openai --version v2-debug --suite base --eval-cases analysis/eval_v1_failing.json --runs-dir analysis/debug_runs
```

Hien tai: 0/3 PASS. Khi 3/3 PASS thi bao Nguoi 1 chay full base `v2` de kiem tra regression.

## Luu y cho vong sau

- Chay v2 sau khi ca hai merge, cung provider/model va `data/eval_base.json`.
- Sau khi base on dinh, nen chay them extension/adversarial de kiem tra policy, external search va fake confirmation.
