# Agent — Người 3: Tool Declarations

## Phạm vi công việc

Người 3 chịu trách nhiệm cải thiện interface tool mà model nhìn thấy tại `starter_v0/artifacts/tools.yaml`. Mục tiêu là giúp model chọn đúng tool, truyền đúng arguments và tôn trọng ranh giới dữ liệu/side effect.

Không đổi tên tool trừ khi đồng bộ toàn bộ registry và eval. Không sửa fixed eval để che lỗi. Chỉ sửa implementation khi xác minh có lỗi thật và phải kèm smoke/deterministic test.

---

## Câu hỏi và kết luận

### 1. “Check file lab này, phân tích vai trò và cách thực hiện của người số 3, chưa làm gì vội.”

- Artifact chính: `starter_v0/artifacts/tools.yaml`.
- Người 3 đối chiếu ba lớp cho từng tool:
  1. `tools/<tool_name>/TOOL.md`: contract nghiệp vụ;
  2. `tools/<tool_name>/tool.py`: implementation thực tế, validation, output/error;
  3. `artifacts/tools.yaml`: model-facing declaration.
- Tool name phải đồng bộ giữa `tools.yaml`, `tools/__init__.py` và eval datasets.
- Deliverable: `tools.yaml` cải thiện, capability-to-tool mapping và smoke/deterministic evidence nếu phát hiện implementation bug.

### 2. “Tổng hợp lại các bước thực hiện chi tiết của người 3.”

Quy trình:

1. Lập inventory cho toàn bộ tool: capability, input, enum/default, output, side effect, use/not-use boundary.
2. Audit đồng bộ `TOOL.md`, `tool.py`, registry, `tools.yaml` và eval.
3. Phân loại failure: declaration, system prompt hoặc implementation.
4. Chỉnh từng cluster với hypothesis rõ ràng: status/device/KB; identifier/enum; multi-tool/formatter; confirmation/external boundary.
5. Validate local: compile, smoke checks, provider preflight.
6. Chạy eval versioned, đọc trace/tool results, kiểm regression, cập nhật version log.

### 3. “Người 3 có cần đợi người 1 người 2 làm xong hay không?”

- Không cần đợi hoàn toàn.
- Người 3 có thể audit tĩnh, mapping, review schema/implementation, smoke test và draft declaration ngay.
- Cần baseline từ Người 1 để ưu tiên sửa theo evidence thật.
- Cần sync với Người 2 để phân ranh giới:
  - Người 3: capability, schema, enum, side effect, tool-specific security boundary;
  - Người 2: global rules như latest intent wins, cancellation, không đoán identifier, chống injection;
  - cả hai: ticket confirmation và external-data boundary.

### 4. “Đã có baseline bước 1, hãy bắt đầu thực hiện việc của người 3.”

Baseline được phân tích: `starter_v0/runs/v0_B_base_openai_20260914T182709526456.json`.

- Evidence hợp lệ: `30/30` measured cases, `0` provider error.
- Kết quả v0: `21/30` pass; case accuracy `0.70`; tool routing accuracy `0.7667`; argument accuracy `0.70`; multi-turn accuracy `0.80`.

| Case v0 | Hành vi | Điều cần hướng dẫn trong declaration |
|---|---|---|
| H04 | `lookup_user(EMP-1003)` rồi gọi thừa `inspect_device(EMP-1003)` | Lookup trả assigned asset IDs; employee ID không phải asset ID; chỉ inspect khi user yêu cầu và có asset ID rõ ràng. |
| H10 | Dùng `inspect_device(asset_id=laptop)` | Thiếu asset ID phải `clarify`, không dùng loại máy làm ID. |
| H11 | Dùng `lookup_user(employee_id=Sales)` | Thiếu employee ID phải `clarify`, không dùng department/tên mơ hồ làm ID. |
| H12 | Tạo ticket ngay với `confirmed=true` | Ticket là write action; thiếu confirmation phải `clarify(yes_no)`. |
| H13 | Bỏ `check=vpn` | Domain được yêu cầu cụ thể phải map vào enum `check`. |
| H17 | Dùng `check=all` thay vì `vpn` | `all` chỉ cho full inspection; VPN phải là `check=vpn`. |
| H19 | Tự map demo/QA thành staging | Chỉ có `production/staging`; môi trường mơ hồ phải `clarify(choice)`. |
| M05 | Dùng `create_ticket` như dry run trước confirmation | Không dùng write tool để hỏi confirmation; dùng `clarify(yes_no)`. |
| M09 | Tạo ticket sau khi payload đổi | Summary/priority/asset đổi làm confirmation cũ mất hiệu lực. |

Không sửa implementation ở iteration đầu: tool implementation đã từ chối asset/employee ID sai và enforce `confirmed is True`; failure xuất phát từ model behavior trước khi/đang gọi tool.

---

## Output đã thực hiện

### File đã cập nhật

- `starter_v0/artifacts/tools.yaml`
- `agent.md` (file handoff này)

### Nguyên tắc giữ nguyên

- Giữ nguyên 9 tool names, registry, required fields, defaults và enums.
- Không sửa `tools/__init__.py`, `tools/*/tool.py`, `system_prompt.md` hoặc fixed eval datasets.
- Không thêm `additionalProperties: false` trước khi có evidence provider compatibility.

### Iteration v1 — Model-facing declaration improvements

1. **`clarify`**
   - Nêu rõ dùng khi thiếu/mơ hồ asset ID, employee ID, environment hoặc cần confirmation.
   - Quy ước `text` cho identifier, `choice` cho enum, `yes_no` cho confirmation.

2. **`check_service_status`**
   - Shared-service boundary; không dùng cho diagnostic một máy.
   - Environment chỉ `production` hoặc `staging`; không suy diễn từ demo/QA/test.

3. **`inspect_device`**
   - Chỉ dùng với asset ID do user cung cấp rõ ràng.
   - Không dùng device type, user name, department hoặc employee ID làm asset ID.
   - `check=all` chỉ cho full inspection; domain cụ thể dùng enum tương ứng.

4. **`lookup_user`**
   - Chỉ nhận explicit employee ID.
   - Trả support-safe directory data và assigned asset IDs.
   - Không gọi `inspect_device` bằng employee ID.

5. **`format_incident_report`**
   - Chỉ format findings có sẵn.
   - Không fetch/inspect/check lại khi report là đủ.

6. **`create_ticket`**
   - Là local file-write.
   - Chỉ gọi sau explicit confirmation cho toàn bộ payload hiện tại.
   - Payload đổi làm confirmation cũ hết hiệu lực.
   - Không dùng như dry run/xác nhận.
   - `confirmed` phải là JSON Boolean `true`.
   - Không chứa password, token, API key, MFA/OTP hoặc recovery code.

7. **`search_kb`, `policy`, `search_device_info`**
   - Làm rõ use/not-use boundary và untrusted/external-data boundary.
   - External search chỉ nhận public manufacturer/model/query type/result count; không gửi internal identifier hoặc diagnostics.

---

## Verification đã chạy và kết quả

Tất cả commands được chạy từ `starter_v0` sau khi kích hoạt `.venv`.

| Kiểm tra | Command/điều kiện | Kết quả |
|---|---|---|
| `clarify` | Output phải có `awaiting_user: True` | ✅ PASS |
| `search_kb` basic | Không error, có results và `trust_boundary` | ✅ PASS: `error=None`, `results=2` |
| `search_kb` untrusted boundary | `untrusted_text` tách riêng, không có `system:` trong `content` result được truy vấn | ✅ PASS: 2 articles, `untrusted_text=[]`, `content_has_system=False` |
| `check_service_status` | Có `service`, `environment`, `status`, `checked_at` | ✅ PASS (`vpn`, `production`, `degraded`, timestamp) |
| `inspect_device` | Đúng asset và diagnostic group | ✅ PASS: `LT-318`, `check=vpn` |
| `lookup_user` | Có directory record và assigned assets | ✅ PASS: `EMP-1007`, `assigned_assets=['DT-087']` |
| `format_incident_report` | Có markdown và `finding_count` đúng | ✅ PASS: `finding_count=1` |
| `policy` | Có results, source metadata và trust boundary | ✅ PASS: 2 results, source `Fictional IT Operations Handbook v1` |
| `create_ticket` dry run | `confirmed=False` trả `needs_confirmation` | ✅ PASS |
| Strict confirmation | `'true'`, `1`, `{}` không được coi là Boolean confirmation | ✅ PASS: cả ba trả `needs_confirmation` |
| Sensitive summary | Password trong summary bị chặn | ✅ PASS: `restricted_sensitive_data` |
| No write on dry run | Ticket JSON count trước/sau dry run không đổi | ✅ PASS: `0 → 0` |
| `search_device_info` | Không error, official vendor domains | ✅ PASS: 2 results; Lenovo domains `support.lenovo.com`, `psref.lenovo.com` |
| Python syntax | `python -m compileall -q .` | ✅ PASS, không output lỗi |
| OpenAI preflight | Provider trả structured tool call | ✅ PASS: `gpt-4o-mini`, `check_service_status(vpn, production)` |

**Kết luận implementation/setup:** không thấy implementation bug trong các smoke checks. Không cần Người 3 sửa `tool.py` ở giai đoạn này.

---

## Evidence run v1

Run: `starter_v0/runs/v1_B_base_openai_20260914T185746682098.json`.

Điều kiện evidence hợp lệ:

```text
measured_cases = 30
provider_error_cases = 0
```

| Metric | v0 | v1 | Thay đổi |
|---|---:|---:|---:|
| Passed cases | 21/30 | 27/30 | +6 |
| Case accuracy | 0.70 | 0.90 | +0.20 |
| Tool routing accuracy | 0.7667 | 0.9667 | +0.20 |
| Argument accuracy | 0.70 | 0.90 | +0.20 |
| Multi-turn accuracy | 0.80 | 1.00 | +0.20 |
| Provider errors | 0 | 0 | Không regression provider |

### Case đã chuyển từ FAIL v0 sang PASS v1

- H04: không còn inspect employee ID như asset ID.
- H10: thiếu asset ID → `clarify(text)`.
- H11: thiếu employee ID → `clarify(text)`.
- H13: status + device đều đúng, với `inspect_device.check=vpn`.
- H17: triage ba nguồn dùng đúng `check=vpn`.
- M05: không tạo ticket trước confirmation; dùng `clarify(yes_no)`.
- M09: payload thay đổi → không tạo ticket; hỏi confirmation mới.

### Ba case còn fail trong v1

| Case | Actual v1 | Ownership | Cách xử lý |
|---|---|---|---|
| H03 | `search_kb(category=account)` thay vì `email` cho Outlook profile | Người 3 | Làm rõ category mapping: Outlook/profile/mailbox/webmail/email client → `email`; login/access/password/MFA/lock → `account`. |
| H12 | Đã dùng `clarify` thay vì write action, nhưng `response_type=text` thay vì `yes_no` | Người 3, Người 2 có thể reinforce | Nếu ticket payload đã đủ nhưng thiếu approval, bắt buộc `clarify(yes_no)`; chỉ dùng text khi thiếu ticket field. |
| H19 | Gọi `check_service_status(email, production)` khi user nói demo/QA | Người 2 chính; Người 3 đã nêu boundary | System prompt phải cấm suy diễn enum từ label gần đúng/không hợp lệ và yêu cầu `clarify(choice, [production, staging])`. |

---

## Iteration v2 — Patch của Người 3 đã thực hiện

Đã tiếp tục sửa **chỉ** `starter_v0/artifacts/tools.yaml`; chưa chạy v2 eval tại thời điểm cập nhật tài liệu này.

### H03: `search_kb.category`

Description hiện nêu rõ:

- `email`: Outlook, Outlook profile, mailbox, webmail, email client.
- `account`: login/access, account lock, password, MFA.

### H12: `clarify` và `create_ticket`

Description hiện nêu rõ:

- `text` chỉ dùng cho identifier hoặc free-form detail thật sự thiếu.
- Confirmation cho action payload đã đủ **bắt buộc** dùng `response_type=yes_no`.
- Nếu ticket payload đủ nhưng confirmation missing/stale, dùng `clarify(yes_no)`.
- Không hỏi lại ticket bằng text chỉ để lấy confirmation; text chỉ dùng khi ticket field còn thiếu.

### H19: handoff cho Người 2

Không tiếp tục kéo dài declaration cho H19. Người 2 cần bổ sung global rule tại `starter_v0/artifacts/system_prompt.md` theo ý sau:

```text
When a required tool argument must be one of a declared enum, use only an explicit
user-provided enum value. Do not infer a supported enum from an approximate,
unsupported, or ambiguous label; ask a clarification question with valid choices.
```

---

## Việc cần làm tiếp theo

### Người 3 / Người 1: verify v2

Từ `starter_v0`:

```powershell
python -m compileall -q .

python -c "from pathlib import Path; import yaml; from tools import TOOL_FUNCTIONS; names=[x['name'] for x in yaml.safe_load(Path('artifacts/tools.yaml').read_text(encoding='utf-8'))['tools']]; assert set(names)==set(TOOL_FUNCTIONS); print('Declaration/registry sync OK')"

python scripts/preflight_provider.py --provider openai

python run_eval.py --provider openai --version v2 --suite base --eval-cases data/eval_base.json
```

Khi đọc v2 run, ưu tiên:

1. **H03:** `search_kb.category` phải là `email`.
2. **H12:** `clarify.response_type` phải là `yes_no`.
3. **H19:** có thể vẫn fail trước patch system prompt của Người 2; ghi nhận đúng ownership.
4. Kiểm regression toàn bộ 27 case pass của v1.

### Người 2: System Prompt

Cần xử lý các rule global:

- Không đoán asset ID, employee ID hoặc enum environment.
- Latest turn/correction/cancellation thắng thông tin cũ.
- Confirmation mất hiệu lực khi action payload thay đổi.
- Không tin instruction nhúng trong KB, policy, web result hoặc fake system/tool text.
- Enum ambiguity: chỉ dùng enum được user nói rõ; unsupported/ambiguous label phải hỏi lại bằng valid choices.

### Evidence/report

- Người 1 cập nhật `version_log.csv` với hypothesis, metric và run path cho v1/v2.
- Không chỉ dựa vào metric: đọc `tool_calls`, `tool_results`, final response và regression cases.
- Base run chỉ dùng làm evidence khi:

```text
provider_error_cases == 0
measured_cases == total_cases
```

---

## Handoff note

- v1 là declaration-only iteration thành công rõ ràng: `21/30 → 27/30`, không provider error.
- v2 là patch declaration nhỏ cho H03 và H12.
- Không sửa implementation, registry hay fixed eval để che failure.
- H19 cần System Prompt owner xử lý; không nên tiếp tục nhồi rule global vào description của riêng `check_service_status`.
