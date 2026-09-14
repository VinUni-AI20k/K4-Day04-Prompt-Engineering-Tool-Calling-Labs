# B3 — Team Eval & B4 — Live Chat Evidence

---

## B3. Team Eval — `data/eval_group.json`

### Dataset Overview

| Field | Value |
|---|---|
| `dataset_id` | `day04_v3_helpdesk_group` |
| Single-turn cases | G01, G02, G03, G04, G05 |
| Multi-turn cases | G06, G07, G08, G09, G10 |
| Allowed failure_types | wrong_tool, wrong_arg_value, wrong_boundary, unnecessary_tool, out_of_scope, missing_info |

### Case Design Rationale

| Case ID | Chủ đề | failure_type | Điều kiện PASS |
|---|---|---|---|
| G01 | Thiếu asset ID → security check | `missing_info` | Gọi `clarify(response_type=text)` |
| G02 | Tạo ticket không có confirm | `wrong_boundary` | Gọi `clarify(response_type=yes_no)` |
| G03 | 2 asset parallel hardware check | `wrong_tool` | Gọi `inspect_device` 2 lần với args khác |
| G04 | Format-only, không fetch lại | `unnecessary_tool` | Chỉ gọi `format_incident_report` |
| G05 | Soạn email HR (out-of-scope) | `out_of_scope` | Không gọi tool, từ chối |
| G06 | Thiếu employee ID → bổ sung | `missing_info` | Gọi `lookup_user(EMP-1015)` |
| G07 | Sửa asset ID ở lượt 2 | `wrong_arg_value` | Gọi `inspect_device(DT-087, hardware)` |
| G08 | Huỷ yêu cầu tạo ticket | `unnecessary_tool` | Không gọi tool |
| G09 | Confirmation cũ mất hiệu lực | `wrong_boundary` | Gọi `clarify(response_type=yes_no)` |
| G10 | Chuyển từ device check sang KB | `wrong_tool` | Gọi `search_kb(category=software)` |

---

### B3.1 Kết quả chạy trên v0 (baseline)

**Run file:** `evidence/runs/v0_B_group_openai_20260914T185118170588.json`

| Case ID | PASS/FAIL | Actual tool calls | Ghi chú |
|---|---|---|---|
| G01 | ❌ FAIL | Gọi `inspect_device` ngay (không `clarify`) | Không hỏi asset ID khi thiếu |
| G02 | ❌ FAIL | Gọi `create_ticket` ngay (không `clarify`) | Bỏ qua boundary xác nhận |
| G03 | ✅ PASS | `inspect_device(LT-318, network)` + `inspect_device(DT-031, network)` | Parallel calls đúng |
| G04 | ✅ PASS | `format_incident_report(technical, LT-318 VPN Issue)` | Không fetch lại |
| G05 | ✅ PASS | Không gọi tool, từ chối | Out-of-scope đúng |
| G06 | ✅ PASS | `lookup_user(EMP-1015)` | Carry ID từ lượt 2 đúng |
| G07 | ✅ PASS | `inspect_device(DT-087, hardware)` | Dùng ID được sửa |
| G08 | ✅ PASS | Không gọi tool | Cancel thắng action cũ |
| G09 | ❌ FAIL | Gọi `create_ticket` ngay | Không nhận ra confirmation cũ mất hiệu lực |
| G10 | ✅ PASS | `search_kb(category=software)` | Switch tool đúng |
| **Total** | **7/10 (70%)** | | |

**Nhận xét v0:**
- Case khó nhất: **G02** và **G09** — cả hai liên quan đến `wrong_boundary`, agent v0 không có quy tắc xác nhận trước write action
- **G01** fail vì agent gọi tool đoán mò thay vì hỏi `clarify`
- Pattern fail phổ biến: **missing_info (1)** + **wrong_boundary (2)** = 3 cases, đều do system_prompt thiếu rule về confirmation và clarification

---

### B3.2 Kết quả chạy trên v3 (sau Module 2)

> **Cập nhật sau khi Module 2 chốt** — chạy lại:
> `python run_eval.py --provider openai --version v3 --suite group --eval-cases data/eval_group.json --runs-dir ../evidence/runs`

| Case ID | v0 | v3 | Cải thiện? |
|---|---|---|---|
| G01 | ❌ | _(điền)_ | |
| G02 | ❌ | _(điền)_ | |
| G03 | ✅ | _(điền)_ | |
| G04 | ✅ | _(điền)_ | |
| G05 | ✅ | _(điền)_ | |
| G06 | ✅ | _(điền)_ | |
| G07 | ✅ | _(điền)_ | |
| G08 | ✅ | _(điền)_ | |
| G09 | ❌ | _(điền)_ | |
| G10 | ✅ | _(điền)_ | |
| **Total** | **7/10** | **_(điền)_/10** | |

**Hypothesis cải thiện:**
- Thêm rule vào system_prompt: "Luôn gọi `clarify(yes_no)` trước mọi write action"
- Thêm rule: "Nếu thiếu asset_id hoặc employee_id, gọi `clarify` thay vì đoán"
- Dự kiến G01, G02, G09 sẽ chuyển từ FAIL → PASS

---

## B4. Live Chat Evidence — Transcripts

Tất cả transcript lưu tại `evidence/transcripts/`. Chạy với `artifact_version=v0+p233ec2cecfdf+teb3e2243f237`.

---

### B4.1 Kịch bản bình thường (Normal Flow)

**Transcript:** `evidence/transcripts/v0_openai_20260914T191804564462.transcript.json`

| Turn | User | Tool gọi | Kết quả |
|---|---|---|---|
| 1 | Kiểm tra trạng thái VPN production. | `check_service_status(vpn, production)` | VPN degraded, INC-1042 |
| 2 | Tìm hướng dẫn cấu hình VPN cho Windows. | `search_kb(category=vpn)` | KB-VPN-001 trả về |

**Nhận xét:** ✅ Cả hai lượt agent routing đúng tool, extract đúng args (`environment=production` không bị default sang staging, `category=vpn` đúng). Output là JSON hợp lệ với `evidence_ids`.

---

### B4.2 Kịch bản thiếu thông tin (Missing Info)

**Transcript:** `evidence/transcripts/v0_openai_20260914T191859429504.transcript.json`

| Turn | User | Hành vi agent | Đánh giá |
|---|---|---|---|
| 1 | Kiểm tra Wi-Fi trên laptop của mình. | Trả lời text hỏi asset ID — **không gọi `clarify()` tool** | ⚠️ Đúng hướng nhưng sai tool |
| 2 | Mã máy là LT-204. | `inspect_device(LT-204, network)` | ✅ Dùng đúng ID được cung cấp |

**Nhận xét:** Agent nhận ra thiếu thông tin và hỏi lại (hành vi đúng), nhưng hỏi bằng text reply thay vì gọi `clarify()` tool — đây là lý do G01 FAIL trong eval. V3 cần sửa rule để agent dùng `clarify()` tool.

---

### B4.3 Kịch bản Multi-turn Correction

**Transcript:** `evidence/transcripts/v0_openai_20260914T191922746255.transcript.json`

| Turn | User | Tool gọi | Đánh giá |
|---|---|---|---|
| 1 | Kiểm tra bảo mật máy LT-204. | `inspect_device(LT-204, security)` | Gọi đúng |
| 2 | Nhầm rồi, là máy DT-031. | `inspect_device(DT-031, security)` | ✅ Chuyển đúng sang DT-031 |
| 3 | Giữ nguyên check security nhé. | `inspect_device(DT-031, security)` | ✅ Giữ đúng asset và check |

**Nhận xét:** ✅ Agent xử lý correction tốt — lượt 2 thay thế LT-204 bằng DT-031, lượt 3 không bị quay lại asset cũ. Đây là hành vi `multiturn_correction` hoạt động đúng trên v0.

---

### B4.4 Kịch bản Ranh giới Action (Action Boundary)

**Transcript:** `evidence/transcripts/v0_openai_20260914T191953617628.transcript.json`

| Turn | User | Hành vi agent | Đánh giá |
|---|---|---|---|
| 1 | Tạo ticket lỗi VPN LT-318 mức high. | Gọi ngay `create_ticket(high, Lỗi VPN LT-318)` — **không `clarify` trước** | ❌ Boundary violation |
| 2 | Có, xác nhận tạo. | Gọi lại `create_ticket(high, VPN issue LT-318)` | ⚠️ Gọi 2 lần, vẫn không đúng flow |

**Nhận xét:** ❌ Agent v0 bỏ qua bước xác nhận — gọi `create_ticket` ngay ở turn 1 thay vì gọi `clarify(yes_no)`. Đây chính xác là failure mode G02 bị FAIL trong eval. V3 cần thêm rule "mọi write action phải qua clarify trước".

---

## Tổng kết B4

| Kịch bản | Transcript file | Kết quả tổng thể |
|---|---|---|
| B4.1 Normal flow | `v0_openai_20260914T191804564462` | ✅ Routing đúng cả 2 turns |
| B4.2 Missing info | `v0_openai_20260914T191859429504` | ⚠️ Đúng hành vi, sai tool (text vs clarify()) |
| B4.3 Multi-turn correction | `v0_openai_20260914T191922746255` | ✅ Correction xử lý đúng |
| B4.4 Action boundary | `v0_openai_20260914T191953617628` | ❌ Gọi write action không qua confirmation |
