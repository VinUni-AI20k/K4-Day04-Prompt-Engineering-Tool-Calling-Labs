# Evaluation & Evidence Log — Thành viên 3

## Mục tiêu

Theo dõi bộ team eval G01–G10, tính hợp lệ của từng run, failure analysis và dữ liệu bàn giao cho `version_log.csv`/`REPORT.md`. Chỉ ghi metric chính thức khi run có:

```text
provider_error_cases == 0
measured_cases == total_cases
```

## 1. Kiểm tra team eval

File: `data/eval_group.json`

| Kiểm tra | Kết quả |
|---|---:|
| Tổng số case | 10 |
| Single-turn (`G01–G05`) | 5 |
| Multi-turn (`G06–G10`) | 5 |
| ID duy nhất | 10/10 |
| Failure type không hợp lệ | 0 |
| Tool name không khai báo | 0 |

Các capability được kiểm tra:

- routing tách biệt giữa shared service và single asset;
- thiếu/mơ hồ environment;
- format-only và extra-tool boundary;
- internal policy và external-search privacy boundary;
- correction, cancellation và latest intent;
- hai asset dùng cùng tool với arguments khác nhau;
- confirmation mất hiệu lực khi payload thay đổi;
- phối hợp user lookup và asset inspection.

## 2. Trạng thái baseline hiện tại

Baseline chính thức dùng Gemini, đo đủ 30/30 case, không có provider error và đạt `case_accuracy = 0.70`:

`runs/v0_B_base_gemini_20260914T203716878801.json`

Các run khác provider/model không được trộn vào chuỗi so sánh chính thức `v0–v3`.

## 3. Lệnh kiểm tra local

Chạy từ `starter_v0/` trong terminal đã kích hoạt `.venv`:

```powershell
python -m compileall -q .
python -c "import json; from pathlib import Path; d=json.loads(Path('data/eval_group.json').read_text(encoding='utf-8')); c=d['cases']; print({'total':len(c),'single':sum('turns' not in x for x in c),'multi':sum('turns' in x for x in c),'unique_ids':len({x['id'] for x in c})})"
```

Kết quả mong đợi:

```text
{'total': 10, 'single': 5, 'multi': 5, 'unique_ids': 10}
```

## 4. Lệnh chạy evidence

Thay `<PROVIDER>` bằng đúng provider đã preflight PASS và dùng cùng provider/model cho `v0–v3`.

```powershell
python scripts/preflight_provider.py --provider <PROVIDER>
python run_eval.py --provider <PROVIDER> --version v0 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider <PROVIDER> --version v3 --suite group --eval-cases data/eval_group.json
```

Sau mỗi thay đổi artifact, chạy lại base với version tương ứng:

```powershell
python run_eval.py --provider <PROVIDER> --version v1 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider <PROVIDER> --version v2 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider <PROVIDER> --version v3 --suite base --eval-cases data/eval_base.json
```

Lưu ý: `--suite` chỉ là nhãn lưu trong run; `--eval-cases` mới chọn dataset thực tế. Không ghép sai hai tham số.

## 5. Bảng run hợp lệ

Chỉ thêm run vào bảng này sau khi kiểm tra JSON.

| Version | Suite | Provider/model | Total | Measured | Provider errors | Accuracy | Artifact version | Run file | Hợp lệ? |
|---|---|---|---:|---:|---:|---:|---|---|---|
| v0 | base | Gemini / gemini-3.5-flash-lite | 30 | 30 | 0 | 0.7000 | `v0+p27467914bc4d+t86e19195220e` | `runs/v0_B_base_gemini_20260914T203716878801.json` | Có |
| v1 | base | Gemini / gemini-3.5-flash-lite | 30 | 30 | 0 | 0.8667 | `v1+p2150ff37bf0e+t86e19195220e` | `runs/v1_B_base_gemini_20260914T204109346342.json` | Có |
| v2 | base | Gemini / gemini-3.5-flash-lite | 30 | 30 | 0 | 0.8333 | `v2+pc4abc6044ef0+t86e19195220e` | `runs/v2_B_base_gemini_20260914T215004856473.json` | Có |
| v3 | base | Gemini / gemini-3.5-flash-lite | 30 | 30 | 0 | 0.9667 | `v3+p6a2f075953bc+t86e19195220e` | `runs/v3_B_base_gemini_20260914T215515008973.json` | Có |
| v3 | group | OpenRouter / openai/gpt-4o-mini | 10 | 10 | 0 | 0.9000 | `v3+paa2fef2a92ae+teb3e2243f237` | `runs/v3_B_group_openrouter_20260914T233516261660.json` | Có |
| v3 | extension |  | 10 |  |  |  |  |  |  |
| v3 | adversarial |  | 12 |  |  |  |  |  |  |

Run group cũ `runs/v0_B_group_openrouter_20260914T202609795676.json` dùng phiên bản dataset trước khi ma trận G01–G10 được hiệu chỉnh, nên chỉ là diagnostic lịch sử và **không còn được dùng làm evidence**.

### Review thủ công group v3

- Kết quả grader: 9/10 case PASS; `tool_routing_accuracy=0.90`, `argument_accuracy=0.90`, `multiturn_accuracy=1.00`.
- G02 FAIL: expected `clarify`, actual `check_service_status(service=sso, environment=staging)`. Model tự ánh xạ “sandbox” thành staging; đây là `missing_info`/boundary failure cần chuyển cho A/B.
- G05 PASS theo grader và payload chỉ gồm `manufacturer`, public `model`, `query_type`; không có asset/employee ID hay diagnostics. Tuy nhiên tool result trả `missing_api_key`, nên case này **chưa chứng minh external lookup chạy thành công**.
- Chín case còn lại không có tool runtime error. G07 không gọi tool đúng yêu cầu cancellation. G09 chỉ gọi `clarify`, không tạo ticket.
- Run dùng OpenRouter trong khi chuỗi base chính thức dùng Gemini; metric group được báo cáo độc lập, không dùng để tính mức cải thiện `v0–v3`.

## 6. Review failure thủ công cho chuỗi base v0–v3

| Version | Failed cases | Nhận định từ actual calls/tool results |
|---|---:|---|
| v0 | 9 | Thiếu structured tool call ở format/multi-turn; tạo ticket hoặc tự chọn environment thay vì clarify; correction/latest intent chưa ổn định. |
| v1 | 4 | Structured tool calling cải thiện rõ; còn sai boundary ở H12/M05, tự chọn staging ở H19 và gọi policy thay vì xác nhận payload mới ở M09. |
| v2 | 5 | H17 regression do `inspect_device.check=all`; H12/M05 vẫn sai confirmation; H19 vẫn tự chọn environment; M09 gọi clarify nhưng sai `response_type`. |
| v3 | 1 | H11 gọi đúng `clarify` nhưng thiếu argument tường minh `response_type=text`; đây là mismatch argument, không phải sai routing. |

Không thấy `tool_results` báo runtime error trong các failed trace trên. Final response trong run có thể rỗng khi vòng tool-calling kết thúc ở tool call; vì vậy kết luận chỉ dựa trên grader được ghi rõ, không suy rộng sang chất lượng câu trả lời cuối.

## 7. Xuất bảng phân tích

Sau khi có run hợp lệ:

```powershell
python scripts/parse_runs.py runs --output runs/run-analysis.csv
```

Mở `runs/run-analysis.csv` và lọc `passed=False`, sau đó đối chiếu lại từng case trong run JSON.

`runs/run-analysis.csv` đã được tái xuất từ toàn bộ run hiện có, gồm 260 dòng case-level.

## 8. Mẫu failure analysis

```text
Case:
Version/suite:
Expected calls:
Actual calls:
Observed mismatch:
Tool execution result:
Final response:
Giả thuyết nguyên nhân:
Artifact dự định sửa:
Metric dự kiến thay đổi:
Rủi ro regression:
Run file:
```

Phân biệt:

- `case_failure_type`: loại failure mà case được thiết kế để kiểm tra;
- `result.failure_type`: lỗi thực tế của lần chạy;
- `provider_error`: lỗi provider, không phải bằng chứng lỗi prompt/schema;
- PASS routing vẫn cần review thủ công nếu tool result error/rỗng hoặc final response diễn giải sai.

## 9. Dữ liệu cần ghi vào version log

Chỉ cập nhật `artifacts/version_log.csv` sau khi người sửa artifact xác nhận hypothesis và có run hợp lệ:

```text
version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,
reason,hypothesis,metric_name,metric_before,metric_after,run_file
```

Quy tắc:

- `v0`: baseline, để trống `metric_before`;
- `v1–v3`: metric trước/sau phải lấy từ run JSON hợp lệ;
- `artifact_version`, `prompt_hash`, `tools_hash` phải sao chép từ đúng run;
- không tự đặt metric, hash, hypothesis hoặc run path;
- không so sánh các version chạy bằng provider/model khác nhau.

## 10. Bàn giao cho các thành viên

| Người nhận | Nội dung bàn giao |
|---|---|
| A — Prompt | Failure thuộc rule toàn cục, failed trace, metric và regression cases |
| B — Tool Schema | Wrong-tool/wrong-argument traces, expected/actual calls |
| D — UI & Report | Bảng run hợp lệ, version log, G01–G10 result và evidence paths |
| E — Security | Adversarial tool calls/results, ticket filesystem và external boundary cần review |

## 11. Checklist hoàn thành công việc C

- [x] Viết đúng 10 group cases nguyên bản.
- [x] Đúng 5 single-turn và 5 multi-turn.
- [x] ID duy nhất, failure types và tool names hợp lệ.
- [x] Chạy local compile/schema check trong `.venv`.
- [x] Có baseline `v0` hợp lệ: 30/30 measured, 0 provider error.
- [x] Có base run hợp lệ cho `v1`, `v2`, `v3`.
- [x] Có group run `v3` hợp lệ: 10/10 measured, 0 provider error.
- [x] Xuất `runs/run-analysis.csv` và review thủ công failed traces/tool results cho base `v0–v3`.
- [x] Cập nhật `version_log.csv` bằng số liệu thật cho `v0–v3`.
- [x] Bàn giao group failure, privacy payload và tool-result finding cho report/security review trong tài liệu này.
