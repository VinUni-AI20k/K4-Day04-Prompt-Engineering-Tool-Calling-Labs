# B HANDOFF - Tool & Schema Engineer

Ngày: 2026-09-14
Phạm vi: rà soát declaration/schema, registry alignment, Tavily boundary và contract tests.

## 1. Hiện trạng và phần B hoàn thành

Đã đọc README, LAB-GUIDE, TOOL-SETUP, SUBMISSION-GUIDE, system prompt, tools.yaml, registry, 9 implementation/TOOL.md, run hiện có và version log.

Có sẵn trước lượt này:

- 9 tool đã có implementation và registry trong `tools/__init__.py`.
- `artifacts/tools.yaml` là declaration starter; tên tool đã khớp registry.
- Run cũ: `starter_v0/runs/v0_B_base_openrouter_20260914T182527655109.json`.
- `version_log.csv` chỉ có header, chưa có dòng version hợp lệ.

B đã hoàn thành:

- Làm rõ ownership, nguồn dữ liệu, khi dùng/không dùng, side effect và trust boundary trong declaration của cả 9 tool.
- Giữ nguyên toàn bộ tên tool và enum đang được implementation hỗ trợ.
- Làm rõ `create_ticket` là action ghi file, payload confirmation phải là payload cuối cùng, và `confirmed=true` trong args/fake result không tự chứng minh user confirmation.
- Mở rộng guard của `search_device_info`: kiểm tra nội dung manufacturer/model, chặn asset/employee ID, serial, hostname, IP private, location, diagnostics, ticket và secret-like values trước khi dựng request Tavily.
- Thêm deterministic mock test được theo dõi trong `scripts/test_tool_contracts.py`.

## 2. File thay đổi

| File | Lý do |
|---|---|
| `starter_v0/artifacts/tools.yaml` | Chuẩn hóa mô tả capability, ranh giới tool, external data và confirmation; giữ tên/enum/schema tương thích. |
| `starter_v0/tools/search_device_info/tool.py` | Chặn dữ liệu nội bộ theo nội dung giá trị trước `requests.post`; không gửi dữ liệu nhạy cảm thật ra ngoài. |
| `starter_v0/scripts/test_tool_contracts.py` | Test registry/declaration, Tavily mock boundary, missing-key no-network và ticket confirmation/secret rejection. |
| `starter_v0/artifacts/B_HANDOFF.md` | Tài liệu bàn giao phần B. |

Không sửa `system_prompt.md`, fixed eval datasets, agent loop, eval engine, UI hoặc `REPORT.md`.

## 3. Contract ngắn của 9 tool

| Tool | Required/arguments chính | Nguồn và boundary | Side effect |
|---|---|---|---|
| `clarify` | `question`; `response_type`: `text\|yes_no\|choice`; `options` optional | Hỏi thông tin/xác nhận thiếu; không đoán ID | Không |
| `search_kb` | `query`; `category`: `all\|vpn\|email\|wifi\|printing\|account\|security\|hardware\|software\|meeting_room`; `top_k` | Knowledge base local; không inspect live device; retrieved text là untrusted | Không |
| `check_service_status` | `service`: `vpn\|email\|sso\|wifi\|printing`; `environment`: `production\|staging` | Mock shared status page; không chẩn đoán một asset | Không |
| `inspect_device` | `asset_id`; `check`: `all\|network\|vpn\|security\|hardware\|software` | Mock inventory/diagnostics của đúng một asset; không đoán ID | Không |
| `lookup_user` | `employee_id` | Mock employee directory và assigned assets; không đoán ID | Không |
| `format_incident_report` | `findings`, `template`: `brief\|technical\|handoff`, `incident_title` | Chỉ format findings đã có; không tự bịa/điều tra | Không |
| `policy` | `query`; `policy_area`: `all\|access_control\|data_privacy\|external_tools\|incident_response\|service_operations\|ticketing`; `top_k` | Company policy local; text là reference, không phải instruction | Không |
| `create_ticket` | `summary`; `priority`: `low\|medium\|high\|critical`; `asset_id` optional; `confirmed` Boolean | Local ticket store; summary không chứa credential/OTP/recovery code; confirmation phải do user xác nhận payload cuối | Ghi `tickets/` khi `confirmed is True` |
| `search_device_info` | `manufacturer`, `model`, `query_type`: `specs\|drivers\|support\|compatibility`; `max_results` | Tavily; chỉ public product identity; vendor allowlist khi có; web result untrusted | External read-only API |

## 4. Failure analysis và evidence

### Tavily data boundary

- Expected: request body chỉ có manufacturer/model public, query type và giới hạn kết quả; input nội bộ phải bị từ chối trước network.
- Actual trước sửa: implementation chỉ nhận diện regex asset/employee ID; các giá trị như `hostname=...`, `location=...`, IP private, `diagnostic=...` hoặc secret-like text chưa có guard tương ứng.
- Nguyên nhân: boundary kiểm tra tên field chưa đủ; manufacturer/model vẫn là chuỗi tự do.
- Thay đổi: thêm `INTERNAL_DATA_MARKERS` và kiểm tra trên toàn bộ public identity trước kiểm tra API key/request.
- Kết quả: test mock xác nhận 6 nhóm input nội bộ trả `restricted_internal_data` và `requests.post` không được gọi.
- Regression: public model smoke không có Tavily key trả `missing_api_key`, không gọi network; không làm thay đổi các tool local.

### Confirmation và ticket data

- Expected: string `"true"`, số `1`, object fake result hoặc confirmation cũ không được coi là Boolean confirmation; secret không được ghi ticket.
- Actual implementation đã dùng `confirmed is not True` và regex sensitive summary, nên không cần sửa implementation ở lượt này.
- Declaration trước sửa nói quá ngắn, dễ khiến model hiểu `confirmed` là bằng chứng user đã xác nhận.
- Thay đổi: declaration nêu rõ confirmation phải áp dụng cho payload cuối cùng và fake/model-provided state không đủ.
- Kết quả: test với `"true"`, `1`, object và `VPN token: not-real` PASS; không có file ticket được tạo.
- Giới hạn: implementation vẫn có thể tạo ticket nếu caller truyền Boolean `True`; việc chứng minh Boolean đó đến từ explicit user confirmation thuộc agent/system prompt flow. A cần hoàn thiện nguyên tắc toàn cục.

### Registry/schema

- Expected: declaration có đúng 9 tên registry và required fields nằm trong properties.
- Actual sau sửa: 9/9 names match; enum giữ nguyên theo implementation/TOOL.md.
- Test: `test_declarations_match_registry_and_signatures` PASS.

## 5. Lệnh kiểm thử và kết quả

Chạy từ `starter_v0` bằng Python trong `.venv`:

```powershell
.\.venv\Scripts\python.exe -m compileall -q .
.\.venv\Scripts\python.exe -m scripts.test_tool_contracts -v
```

Kết quả thực tế: compile PASS; 8 test PASS.

Local smoke cho 9 tool theo TOOL-SETUP: PASS cho `clarify`, `search_kb`, `check_service_status`, `inspect_device`, `lookup_user`, `format_incident_report`, `policy`, `create_ticket` dry-run và `search_device_info` missing-key path. Không tạo ticket.

Provider preflight đã thử:

```powershell
.\.venv\Scripts\python.exe scripts/preflight_provider.py --provider openrouter
```

Kết quả: BLOCKED, `RuntimeError: Missing API key env var: OPENROUTER_API_KEY`.

Tavily live chưa chạy: `starter_v0/.env` không tồn tại và `TAVILY_API_KEY` không được cấu hình. Không yêu cầu gửi key vào chat và không gửi dữ liệu thật ra ngoài.

Artifact hashes hiện tại:

- `system_prompt.md`: `233ec2cecfdfd80b3879531dfe64e2c1903f39fe0facc08f9bed6fcc064b33f5`
- `tools.yaml`: `503ed3317c4133e71a27444e99fe490fab4195d3db0e450fe0deac2c5e75f9ab`
- local artifact label để tham chiếu: `local-B+p233ec2cecfdf+t503ed3317c41`

Run cũ không hợp lệ làm model evidence:

- `starter_v0/runs/v0_B_base_openrouter_20260914T182527655109.json`
- `total_cases=30`, `measured_cases=0`, `provider_error_cases=30`.
- Không cập nhật `version_log.csv` vì lượt này không có model run hợp lệ và không được tạo version giả.

## 6. Tavily/confirmation review và giới hạn còn lại

Tavily implementation chỉ tạo query từ manufacturer/model/query type, dùng `include_domains` cho vendor đã biết, lọc URL ngoài allowlist và tách instruction-like web text thành `untrusted_text`. Guard mới bổ sung kiểm tra nội dung input trước request. Chưa có live request nên chưa xác nhận behavior với Tavily response thật.

`create_ticket` đã có lớp từ chối kiểu confirmation giả và secret summary. Tuy nhiên Boolean `True` vẫn được tin ở boundary tool; system prompt/agent phải bảo đảm chỉ truyền `True` sau explicit confirmation đúng payload cuối. Đây là đề xuất cho A, không sửa agent loop theo phạm vi B.

## 7. Đề xuất cho các thành viên

### A

- Bổ sung vào system prompt: không tự đoán asset/employee ID; hỏi `clarify` khi thiếu; retrieved KB/policy/web là untrusted; confirmation phải được hỏi lại khi summary/priority/asset thay đổi; không xem tool result/JSON do user cung cấp là confirmation.
- Giữ JSON output contract ổn định và cập nhật version hash sau khi merge declaration mới.

### C

- Thêm/kiểm tra case adversarial cho hostname, private IP, serial, location, diagnostics và secret trong manufacturer/model; expected là không gọi external search.
- Thêm case stale confirmation khi payload ticket thay đổi và review actual tool results, không chỉ PASS/FAIL.

### D

- Hiển thị artifact version/hash và tool args/result/error trong UI; đánh dấu `missing_api_key`, `needs_confirmation`, `restricted_internal_data` là failure/error state chứ không phải thành công.
- Không hiển thị hoặc lưu secret, `.env`, generated ticket trong demo artifact.

## 8. Đang bị chặn

- Chưa chạy provider preflight/eval hợp lệ do thiếu `OPENROUTER_API_KEY`.
- Chưa chạy Tavily live do thiếu `TAVILY_API_KEY`.
- Chưa có metric routing/argument mới; không được suy ra metric từ run provider-error.

Lệnh chạy lại sau khi người có quyền cấu hình key trong môi trường local:

```powershell
cd starter_v0
.\.venv\Scripts\python.exe scripts/preflight_provider.py --provider openrouter
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version B-tools-boundary --suite base --eval-cases data/eval_base.json
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version B-tools-boundary --suite extension --eval-cases data/eval_helpdesk_extension.json
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version B-tools-boundary --suite adversarial --eval-cases data/eval_adversarial.json
```

Chỉ thêm dòng vào `version_log.csv` sau khi run đạt `provider_error_cases == 0` và `measured_cases == total_cases`, đồng thời giữ nguyên các run/log cũ.
