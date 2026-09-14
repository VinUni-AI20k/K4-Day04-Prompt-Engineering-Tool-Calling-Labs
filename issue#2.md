## Parent

#1

## Suggested owner

Role C: Eval & Evidence Engineer

## What to build

Thiết lập baseline v0 đáng tin cậy để cả nhóm cùng dùng làm điểm xuất phát.
Provider phải vượt qua structured tool-calling preflight, các local tools phải chạy được và baseline phải có run evidence cùng failure analysis đại diện.

## Acceptance criteria

- [x] Provider được chọn và preflight structured tool calling thành công. (`openai` / `gpt-5.6-luna`).
- [x] Local tool smoke checks hoàn thành mà không để lại generated ticket rác.
- [x] Base suite v0 được chạy với `provider_error_cases == 0` và `measured_cases == total_cases` (30/30 cases, accuracy 86.67%).
- [x] Run lưu provider, model, dataset, artifact version và hashes (`starter_v0/runs/v0_B_base_openai_20260914T185238636918.json`).
- [x] Ít nhất năm failure đại diện được ghi lại gồm routing, argument, missing information, multi-turn và safety hoặc confirmation (ghi nhận tại `REPORT.md` mục B2).
- [x] Quy ước đặt tên version, run và transcript được ghi rõ để cả nhóm sử dụng (`SHARED-EVIDENCE-RULES.md`).

## Evidence & Outcomes

- **Baseline Run file**: `starter_v0/runs/v0_B_base_openai_20260914T185238636918.json`
- **Artifact Version**: `v0+p233ec2cecfdf+teb3e2243f237` (prompt hash: `233ec2cecfdf`, tools hash: `eb3e2243f237`)
- **Metric**: `case_accuracy` = 0.8667 (26/30 pass, 0 provider error)
- **Version Log**: Đã cập nhật vào `starter_v0/artifacts/version_log.csv`
- **Report**: Đã cập nhật mục B1 và B2 trong `starter_v0/artifacts/REPORT.md`
- **Shared Rules**: Đã ban hành `SHARED-EVIDENCE-RULES.md`

## Blocked by

- None, can start immediately.
