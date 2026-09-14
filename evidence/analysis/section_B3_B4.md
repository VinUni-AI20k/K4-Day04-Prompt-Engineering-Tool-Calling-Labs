# B3 — Team Eval & B4 — Live Chat Evidence

> **Hướng dẫn điền:** Phần này cần được điền sau khi chạy eval và thu transcript.
> Xem [module3_guide.md](../../../.gemini/antigravity-ide/brain/dd24200d-1481-4d97-aa3f-57ef82ad9f8f/module3_guide.md) để biết quy trình.

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

> **Điền sau khi chạy:** `python run_eval.py --provider openai --version v0 --suite group --eval-cases data/eval_group.json --runs-dir ../evidence/runs`

**Run file:** `evidence/runs/v0_B_group_openai_TIMESTAMP.json`

| Case ID | PASS/FAIL | Actual tool calls | Ghi chú |
|---|---|---|---|
| G01 | _(điền)_ | | |
| G02 | _(điền)_ | | |
| G03 | _(điền)_ | | |
| G04 | _(điền)_ | | |
| G05 | _(điền)_ | | |
| G06 | _(điền)_ | | |
| G07 | _(điền)_ | | |
| G08 | _(điền)_ | | |
| G09 | _(điền)_ | | |
| G10 | _(điền)_ | | |
| **Total** | **?/10** | | |

**Nhận xét v0:**
- Case khó nhất (fail trên v0): _(điền)_
- Pattern fail phổ biến: _(điền)_

---

### B3.2 Kết quả chạy trên v3 (sau Module 2)

> **Điền sau khi Module 2 chốt:** `python run_eval.py --provider openai --version v3 --suite group --dataset data/eval_group.json --runs-dir ../evidence/runs`

**Run file:** `evidence/runs/v3_B_group_openai_TIMESTAMP.json`

| Case ID | v0 | v3 | Cải thiện? |
|---|---|---|---|
| G01 | | | |
| G02 | | | |
| G03 | | | |
| G04 | | | |
| G05 | | | |
| G06 | | | |
| G07 | | | |
| G08 | | | |
| G09 | | | |
| G10 | | | |
| **Total** | **?/10** | **?/10** | |

**Phân tích cải thiện:**
- Artifact thay đổi chính: _(system_prompt.md / tools.yaml)_
- Cases nào cải thiện: _(điền)_
- Cases nào vẫn fail: _(điền)_

---

## B4. Live Chat Evidence — Transcripts

> **Yêu cầu:** 4 transcript thu thực tế qua `chat.py`, lưu trong `evidence/transcripts/`

### B4.1 Kịch bản bình thường (Normal Flow)

**Script chat:**
```
You> Kiểm tra trạng thái VPN production.
You> Tìm hướng dẫn cấu hình VPN cho Windows.
You> /exit
```

**Transcript file:** `evidence/transcripts/v0_openai_TIMESTAMP.transcript.json`

**Quan sát:**
- Turn 1: Agent gọi `check_service_status(service=vpn, environment=production)` ✓/✗
- Turn 2: Agent gọi `search_kb(category=vpn)` ✓/✗
- Behavior: _(mô tả)_

---

### B4.2 Kịch bản thiếu thông tin (Missing Info)

**Script chat:**
```
You> Kiểm tra Wi-Fi trên laptop của mình.
[Agent hỏi lại asset ID]
You> Mã máy là LT-204.
You> /exit
```

**Transcript file:** `evidence/transcripts/v0_openai_TIMESTAMP.transcript.json`

**Quan sát:**
- Turn 1: Agent gọi `clarify()` đúng ✓/✗
- Turn 2: Agent gọi `inspect_device(LT-204, network/wifi)` ✓/✗
- Behavior: _(mô tả)_

---

### B4.3 Kịch bản Multi-turn (Sửa thông tin)

**Script chat:**
```
You> Kiểm tra bảo mật máy LT-204.
You> Nhầm rồi, là máy DT-031.
You> Giữ nguyên check security nhé.
You> /exit
```

**Transcript file:** `evidence/transcripts/v0_openai_TIMESTAMP.transcript.json`

**Quan sát:**
- Turn 3: Agent dùng DT-031 (không dùng LT-204 cũ) ✓/✗
- Agent gọi `inspect_device(DT-031, security)` ✓/✗
- Behavior: _(mô tả — agent có bị nhầm sang asset cũ không?)_

---

### B4.4 Kịch bản Ranh giới action (Action Boundary)

**Script chat:**
```
You> Tạo ticket lỗi VPN LT-318 mức high.
[Agent phải hỏi xác nhận]
You> Có, xác nhận tạo.
You> /exit
```

**Transcript file:** `evidence/transcripts/v0_openai_TIMESTAMP.transcript.json`

**Quan sát:**
- Turn 1: Agent gọi `clarify(response_type=yes_no)` (không gọi `create_ticket` ngay) ✓/✗
- Sau confirm: Agent proceed với `create_ticket` ✓/✗
- Behavior: _(mô tả boundary behavior)_

---

## Hướng dẫn cập nhật file này

1. Chạy eval v0 → điền bảng B3.1
2. Chạy 4 kịch bản chat → điền bảng B4.1–B4.4
3. Hoàn thành Module 2 → chạy eval v3 → điền bảng B3.2
4. Viết phân tích so sánh v0 vs v3
