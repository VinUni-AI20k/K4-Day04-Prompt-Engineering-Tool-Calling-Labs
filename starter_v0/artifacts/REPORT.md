# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team:
- Members:
- Provider/model:

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> Viết 1–2 câu mô tả capability và giới hạn của agent.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
<<<<<<< Updated upstream
| clarify | Hỏi bổ sung hoặc xác nhận | core |
|  |  |  |

## A3. Câu hỏi mẫu

1.
2.
3.
=======
| clarify | Hỏi bổ sung thông tin (text/choice) hoặc xin xác nhận (yes_no) | core |
| search_kb | Tìm hướng dẫn kỹ thuật, how-to trong knowledge base nội bộ | core |
| check_service_status | Kiểm tra trạng thái shared service (vpn, email, sso, wifi, printing) | core |
| inspect_device | Kiểm tra chẩn đoán và thông tin tài sản thiết bị (asset_id) | core |
| lookup_user | Tra cứu thông tin danh bạ nhân viên theo employee_id | core |
| format_incident_report | Format các findings đã có sẵn thành báo cáo sự cố chuẩn | core |
| policy | Tra cứu quy chế, chính sách IT nội bộ của công ty | optional built-in |
| create_ticket | Tạo ticket hỗ trợ khi đã có xác nhận rõ ràng (confirmed=true) | optional built-in |
| search_device_info | Tìm thông số, drivers chính hãng trên web qua Tavily Search API | optional built-in |
| diagnose_network | Chẩn đoán chi tiết ping/DNS, đo latency, packet loss, phân giải DNS | team-built (bonus) |

## A3. Câu hỏi mẫu

1. Kiểm tra trạng thái VPN production.
2. Kiểm tra trạng thái VPN production và VPN trên LT-318, sau đó lập báo cáo kỹ thuật với tiêu đề "VPN LT-318".
3. Tạo ticket priority low cho lỗi Outlook chậm trên LT-204.
4. Chẩn đoán chi tiết kết nối ping và DNS tới vpn.northstar.internal.
5. Kiểm tra đo độ trễ và mất gói tin ping tới gateway mặc định từ máy tính DT-087.
>>>>>>> Stashed changes

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Không làm phần này không ảnh hưởng việc hoàn thành core lab. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
<<<<<<< Updated upstream
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

=======
| Optional built-in | `runs/v1_B_extension_gemini_20260914T183159927879.json` | `create_ticket` tạo thành công khi confirmed=True (E05, E08); `policy` tra cứu đúng quy định IT (E01, E04, E06, E07). | Chặn credential trong summary; hủy hiệu lực xác nhận khi thay đổi payload. |
| External search + privacy boundary | `runs/v1_B_extension_gemini_20260914T183159927879.json` | `search_device_info` gọi Tavily Search API thành công (E09, E10), lấy specs và drivers chính hãng từ official vendor domains. | Guardrail nghiêm ngặt: regex `INTERNAL_IDENTIFIER` chặn exfiltration mã asset_id (LT-204) và employee_id; loại bỏ prompt injection từ kết quả web. |
| Bonus: tool mới do nhóm tự xây (`diagnose_network`) | `runs/v3_B_bonus_network_openrouter_20260914T204500123456.json` & `transcripts/v3_bonus_network_diagnostics.transcript.json` | Chẩn đoán ping/DNS chi tiết cho endpoint nội bộ (`vpn.northstar.internal`, `dns.northstar.internal`, `mail`, `gateway`) và external (`8.8.8.8`). Kết hợp góc nhìn thiết bị (`DT-087` phát hiện 12% packet loss tới gateway; `LT-240` phát hiện Wi-Fi gateway tầng 4 unreachable do INC-1045). Smoke test 10/10 PASS (`scripts/test_diagnose_network.py`), team eval 5/5 PASS (`data/eval_bonus_network.json`). Đầy đủ spec `tools/diagnose_network/TOOL.md` và đăng ký trong `tools/__init__.py` & `artifacts/tools.yaml`. | Guardrail 5 lớp: (1) Chặn 100% command/shell injection qua regex `SAFE_TARGET_PATTERN` và kiểm tra ký tự metacharacters (`restricted_command_injection_detected`); (2) Chặn SSRF/loopback/cloud metadata `127.0.0.1`, `localhost`, `169.254.169.254` (`restricted_target_ssrf`); (3) Chặn rò rỉ token/password qua DNS query (`restricted_sensitive_data_in_target`); (4) Đảm bảo read-only non-destructive (`side_effect: false`); (5) Gắn cờ ranh giới tin cậy `trust_boundary` trong output. |

### Chi tiết triển khai Bonus Tool (`diagnose_network`)

- **Thành viên thực hiện**: Nguyễn Xuân Khuê (2A202602999 - Sinonmoe).
- **Hồ sơ năng lực (Capability profile)**:
  - Spec đầy đủ: `tools/diagnose_network/TOOL.md`.
  - Implementation: `tools/diagnose_network/tool.py` và `tools/diagnose_network/__init__.py`.
  - Đăng ký hệ thống: `tools/__init__.py` (`TOOL_FUNCTIONS["diagnose_network"]`).
  - Schema LLM: `artifacts/tools.yaml` (các trường `target`, `check_type`, `asset_id`, `packet_count`).
  - Mock telemetry data: `helpdesk_data/network_diagnostics.json` (tích hợp hạ tầng mạng Northstar Labs, map tương thích với `service_status.json` và `assets.json`).
  - Smoke test: `scripts/test_diagnose_network.py` — **10/10 Test Case PASS** (bao phủ ping, DNS, device context, Wi-Fi outage, và 3 lớp guardrail injection/SSRF/exfiltration).
  - Team eval suite: `data/eval_bonus_network.json` — **5/5 Cases PASS** (`case_accuracy = 1.0`, `provider_error = 0`).
  - Transcript bằng chứng UI/live chat: `transcripts/v3_bonus_network_diagnostics.transcript.json`.
  - Bằng chứng Run evaluation: `runs/v3_B_bonus_network_openrouter_20260914T204500123456.json`.
  - UI compatibility: Streamlit `app.py` tự động nhận diện và hiển thị tool trace, arguments và structured results.
>>>>>>> Stashed changes
## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Reflection chung của nhóm

Các thành viên thảo luận và viết một reflection chung. Nội dung cần dựa trên
evidence thực tế trong repository, không chỉ mô tả cảm nhận chung.

- Mục tiêu nào của nhóm đã hoàn thành? Dẫn đến artifact hoặc run tương ứng.
- Hypothesis hoặc thay đổi nào tạo ra cải thiện rõ nhất?
- Failure quan trọng nào vẫn chưa xử lý được hoàn toàn?
- Nhóm đã phân chia, review và tích hợp công việc như thế nào?
- Nếu có thêm một vòng, nhóm sẽ ưu tiên thay đổi và kiểm chứng điều gì?

**Reflection chung của nhóm:**

> Viết reflection tại đây và dẫn link/path đến evidence liên quan.

## C2. Self-reflection của từng thành viên

Mỗi thành viên tự viết một mục riêng về phần việc chính mình đã thực hiện trong
repository chung. Không viết thay hoặc gộp nhiều thành viên vào một câu trả lời.
Mỗi reflection cần trỏ đến file, commit hoặc pull request có thật để người đọc
có thể đối chiếu đóng góp.

Sao chép mẫu dưới đây cho từng thành viên:

### Họ tên — MSSV

- **Vai trò/phần việc được nhận:**
- **Những gì tôi đã thay đổi trong repo chung:**
- **File hoặc artifact liên quan:**
- **Commit hash hoặc pull request:**
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
- **Khó khăn tôi gặp và cách tôi xử lý:**
- **Điều tôi học được từ phần việc này:**
- **Nếu làm lại, tôi sẽ cải thiện điều gì:**

Mỗi thành viên phải tự commit phần self-reflection của mình bằng Git identity
tương ứng. Reflection phải dẫn đến contribution artifact/commit đã nêu ở trên,
không dùng chính phần reflection làm bằng chứng duy nhất cho đóng góp kỹ thuật.

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAMMATES.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:
