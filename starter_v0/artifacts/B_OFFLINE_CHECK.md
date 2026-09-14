# B Offline Check - Tool & Schema Engineer

Ngày kiểm tra: 2026-09-14
Phạm vi: local/deterministic/mock; không gọi model provider, Tavily hoặc API ngoài.

## Kết luận ngắn

Phần B hiện chạy được các kiểm tra offline. Declaration có 9 tool, tên khớp registry và loader/provider conversion PASS. Local tool behavior, Tavily request boundary bằng mock HTTP và create_ticket trong thư mục tạm PASS. Không có model evidence mới: `OPENROUTER_API_KEY` và `TAVILY_API_KEY` đều chưa cấu hình.

Run trước đó `v0_B_base_openrouter_20260914T182527655109.json` **không phải model evidence hợp lệ**: `total_cases=30`, `measured_cases=0`, `provider_error_cases=30` vì thiếu `OPENROUTER_API_KEY`.

## Bảng kiểm tra

| Hạng mục | Lệnh/test | Kết quả | Evidence |
|---|---|---|---|
| Syntax Python | `.venv\\Scripts\\python.exe -m compileall -q .` | PASS | Compile toàn bộ `starter_v0` không lỗi |
| Registry/declaration | `test_declarations_match_registry_and_signatures` | PASS | 9 declaration names = `TOOL_FUNCTIONS`; required nằm trong properties |
| Provider schema conversion | Cùng test declaration | PASS | `to_openai_tools()` tạo 9 function tools hợp lệ |
| Local tool behavior | `test_local_tools_return_expected_results_and_unknown_ids` | PASS | Kiểm tra kết quả hợp lệ cho 8 local/control tools và unknown IDs |
| Schema enum/runtime boundary | `test_schema_constraints_are_not_runtime_validation` | PASS (phát hiện giới hạn) | Schema mô tả enum nhưng implementation hiện trả `not_found`, giữ giá trị lạ hoặc fallback thay vì luôn reject |
| Tavily internal-data boundary | `test_search_device_info_rejects_internal_values_before_network` | PASS | 6 nhóm serial/hostname/location/private IP/diagnostic/token bị chặn; HTTP mock không được gọi |
| Tavily public request | `test_search_device_info_sends_only_public_query_and_handles_empty_result` | PASS | Mock request body chỉ tạo từ manufacturer/model/query type/max_results; empty result không bị báo thành công giả |
| Tavily missing key | `test_search_device_info_missing_key_does_not_call_network` | PASS | `missing_api_key`, HTTP mock không được gọi |
| Tavily API failure | `test_search_device_info_returns_api_error_without_faking_success` | PASS | Exception trả error, không tạo success result |
| Ticket confirmation | `test_create_ticket_requires_real_boolean_and_rejects_secrets` | PASS | `"true"`, `1`, object => `needs_confirmation`; secret summary bị reject; không ghi file |
| Ticket creation | Cùng test trong `TemporaryDirectory` | PASS | Boolean `True` với payload hợp lệ tạo đúng file/nội dung tạm |
| Full local smoke | Lệnh smoke tổng hợp theo `TOOL-SETUP.md` | PASS | Cả 9 tool chạy trên fixture; create_ticket chỉ dry-run |
| Provider preflight | Không chạy theo yêu cầu offline | CHƯA KIỂM CHỨNG | Không gọi `preflight_provider.py`; key chưa có |
| Tavily live | Không chạy theo yêu cầu offline | CHƯA KIỂM CHỨNG | Không có `TAVILY_API_KEY`, không gọi network |

Lệnh deterministic suite:

```powershell
cd starter_v0
.\\.venv\\Scripts\\python.exe -m scripts.test_tool_contracts -v
```

Kết quả: **8/8 tests PASS**.

## Rà soát 9 tool

| Tool | Declaration/implementation | Offline result |
|---|---|---|
| `clarify` | `question` required; response types được mô tả | PASS output `awaiting_user`; implementation chưa validate `response_type`/options |
| `search_kb` | query/category/top_k khớp signature | PASS hit và trust boundary; category lạ không bị runtime reject |
| `check_service_status` | service/environment enum khớp fixture | PASS status hợp lệ và unknown service `not_found`; enum lạ thành lookup miss |
| `inspect_device` | asset_id/check khớp signature | PASS device/diagnostics và unknown asset; check lạ trả `not_available` |
| `lookup_user` | employee_id required | PASS record và unknown employee `employee_not_found` |
| `format_incident_report` | findings/template/title khớp signature | PASS format findings; template lạ hiện rơi vào brief thay vì reject |
| `policy` | query/policy_area/top_k khớp signature | PASS policy result/trust boundary; area lạ lọc thành empty result |
| `create_ticket` | summary required, priority enum, asset optional, confirmed Boolean | PASS type/priority/asset/secret/confirmation checks trong implementation |
| `search_device_info` | manufacturer/model/query_type/max_results khớp signature | PASS mock boundary, missing key, API error và empty result |

Tên arguments, defaults và enum trong `tools.yaml` đã được đối chiếu với signature/implementation và `TOOL.md`. Required fields là ràng buộc của provider schema: Python functions có default rỗng cho khả năng gọi nội bộ, nên gọi trực tiếp thiếu required argument có thể không bị `TypeError`. Enum trong declaration cũng không tự tạo runtime validation; implementation chỉ validate một số field, còn các trường hợp nêu trên được xử lý như lookup miss, fallback hoặc `not_available`. Đây là giới hạn contract cần nhóm biết, không được coi schema là enforcement của Python.

## Lỗi phát hiện và file đã sửa

1. `search_device_info` trước đây chỉ nhận diện mẫu asset/employee ID. Chuỗi chứa hostname, serial, location, private IP, diagnostics hoặc secret có thể lọt qua. Đã sửa guard nội dung trong `tools/search_device_info/tool.py`; test mock chứng minh request không được tạo.
2. Declaration trước đây mô tả quá ngắn ranh giới giữa shared service/device, KB/policy, external data và ticket confirmation. Đã sửa `artifacts/tools.yaml`.
3. Suite cũ chưa bao phủ provider conversion, đủ 9 direct tools, Tavily API failure/empty response và successful temporary ticket. Đã bổ sung `scripts/test_tool_contracts.py`.

Không phát hiện lỗi mới cần sửa trong `create_ticket`: tool dùng `confirmed is True`, chặn secret summary và chỉ ghi trong temp directory của test.

## Đối chiếu yêu cầu phần B

- [x] 9 tool declaration được loader đọc.
- [x] Tên declaration khớp `tools/__init__.py`.
- [x] Provider tool conversion offline thành công.
- [x] Contract và ranh giới từng tool được rà soát.
- [x] Local valid/unknown ID và format report được kiểm tra.
- [x] Tavily HTTP được mock tại `requests.post`; không có request mạng thật.
- [x] Nội dung serial, asset ID, employee ID, hostname, IP nội bộ, diagnostics và secret-like data được kiểm tra.
- [x] Missing key/API error/empty result được kiểm tra.
- [x] Ticket confirmation, valid creation, secret rejection và temp directory được kiểm tra.
- [x] Ticket có sẵn không bị đụng tới; test không dùng thư mục `tickets/` thật.
- [x] Không sửa agent loop, eval engine, fixed datasets hoặc phần A/C/D.

## Có thể xác nhận offline

- Schema YAML hợp lệ và provider adapter nhận được declaration.
- Tên, field, default/enum declaration theo contract hiện tại.
- Hành vi deterministic của local tools trên mock data.
- Tavily input guard và request body bằng HTTP mock.
- Thiếu key/API failure/empty response không bị báo thành công giả.
- Boolean confirmation ở lớp tool và ghi ticket hợp lệ trong temp directory.

## Chưa thể xác nhận offline

Các nội dung sau cần live model/provider hoặc run hợp lệ, không suy ra từ mock:

- routing của model giữa `check_service_status` và `inspect_device`;
- argument extraction từ ngôn ngữ tự nhiên;
- model có chọn `clarify` khi thiếu ID hay không;
- context carry-over, correction và multi-turn;
- chống prompt injection qua model với KB/policy/web result;
- stale confirmation gắn với payload cuối qua agent/system prompt;
- routing accuracy, argument accuracy, missing/extra calls và các eval metrics;
- structured tool calling từ OpenRouter;
- Tavily live response filtering và vendor results thực tế.

## Checklist bàn giao còn thiếu

- [ ] A cập nhật system prompt về không đoán ID, untrusted content và explicit confirmation theo payload cuối.
- [ ] C chạy adversarial/team eval với provider có key và review actual tool results.
- [ ] D tích hợp hash/artifact version, tool args/results/errors vào UI.
- [ ] Nhóm chạy lại preflight và eval chỉ khi `provider_error_cases == 0` và `measured_cases == total_cases`.
- [ ] Chỉ cập nhật `version_log.csv` bằng run hợp lệ; không dùng run provider-error hiện tại làm metric.

## Artifact/evidence

- Declaration: `starter_v0/artifacts/tools.yaml`
- Implementation guard: `starter_v0/tools/search_device_info/tool.py`
- Deterministic tests: `starter_v0/scripts/test_tool_contracts.py`
- Handoff trước đó: `starter_v0/artifacts/B_HANDOFF.md`
- Run cũ không hợp lệ: `starter_v0/runs/v0_B_base_openrouter_20260914T182527655109.json`
- Current `tools.yaml` SHA-256: `503ed3317c4133e71a27444e99fe490fab4195d3db0e450fe0deac2c5e75f9ab`
- Current `system_prompt.md` SHA-256: `233ec2cecfdfd80b3879531dfe64e2c1903f39fe0facc08f9bed6fcc064b33f5`
