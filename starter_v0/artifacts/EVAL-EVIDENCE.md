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

- routing giữa asset, shared service, policy và formatter;
- thiếu/mơ hồ environment;
- hai lần gọi cùng một tool với arguments khác nhau;
- format-only và extra-tool boundary;
- correction, cancellation và latest intent;
- confirmation mất hiệu lực khi payload thay đổi;
- phối hợp user lookup và asset inspection.

## 2. Trạng thái baseline hiện tại

Các run thử trước đây có `provider_error_cases > 0` do một trong các lỗi cấu hình/quota sau:

- thiếu `OPENROUTER_API_KEY`;
- dùng key không thuộc OpenRouter và nhận HTTP 401;
- Gemini HTTP 429 `RESOURCE_EXHAUSTED` do free-tier rate limit.

Các run này chỉ dùng để chẩn đoán setup, **không dùng làm evidence `v0` và không ghi metric vào `version_log.csv`**.

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
| v0 | base | OpenRouter / openai/gpt-4o-mini | 30 | 30 | 0 | 0.70 | `v0+p233ec2cecfdf+teb3e2243f237` | `runs/v0_B_base_openrouter_20260914T202439651234.json` | Có |
| v1 | base |  | 30 |  |  |  |  |  |  |
| v2 | base |  | 30 |  |  |  |  |  |  |
| v3 | base |  | 30 |  |  |  |  |  |  |
| v3 | group |  | 10 |  |  |  |  |  |  |
| v3 | extension |  | 10 |  |  |  |  |  |  |
| v3 | adversarial |  | 12 |  |  |  |  |  |  |

Diagnostic bổ sung: `runs/v0_B_group_openrouter_20260914T202609795676.json` chạy G01–G10 trên baseline, đạt 9/10 (0 provider error). Đây không thay thế group run `v3` cuối cùng.

## 6. Xuất bảng phân tích

Sau khi có run hợp lệ:

```powershell
python scripts/parse_runs.py runs --output runs/run-analysis.csv
```

Mở `runs/run-analysis.csv` và lọc `passed=False`, sau đó đối chiếu lại từng case trong run JSON.

## 7. Mẫu failure analysis

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

## 8. Dữ liệu cần ghi vào version log

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

## 9. Bàn giao cho các thành viên

| Người nhận | Nội dung bàn giao |
|---|---|
| A — Prompt | Failure thuộc rule toàn cục, failed trace, metric và regression cases |
| B — Tool Schema | Wrong-tool/wrong-argument traces, expected/actual calls |
| D — UI & Report | Bảng run hợp lệ, version log, G01–G10 result và evidence paths |
| E — Security | Adversarial tool calls/results, ticket filesystem và external boundary cần review |

## 10. Checklist hoàn thành công việc C

- [x] Viết đúng 10 group cases nguyên bản.
- [x] Đúng 5 single-turn và 5 multi-turn.
- [x] ID duy nhất, failure types và tool names hợp lệ.
- [x] Chạy local compile/schema check trong `.venv`.
- [x] Có baseline `v0` hợp lệ: 30/30 measured, 0 provider error.
- [ ] Có base run hợp lệ cho `v1`, `v2`, `v3`.
- [ ] Có group run `v3` hợp lệ: 10/10 measured, 0 provider error.
- [x] Xuất và review `runs/run-analysis.csv` cho baseline và group diagnostic.
- [x] Cập nhật dòng `v0` trong `version_log.csv` bằng số liệu thật.
- [ ] Bàn giao evidence cho report và security review.
