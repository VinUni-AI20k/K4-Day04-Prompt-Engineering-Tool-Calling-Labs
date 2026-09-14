# Day 04 Lab v3 Report — IT Helpdesk Agent

> **Trạng thái bản nháp:** Phần đóng góp của thành viên D (UI & Report
> Coordinator) đã được cập nhật từ evidence chạy thật trên v0. Các metric,
> prompt/tool changes, group eval và adversarial evidence vẫn chờ A/B/C cung
> cấp; tài liệu này không tự điền số liệu chưa được kiểm chứng.

## Team

- **Team:** Chờ nhóm cập nhật tên chính thức.
- **Members:** Đặng Quốc Cường (D — UI & Report Coordinator); các thành viên A/B/C chờ nhóm cập nhật.
- **Provider/model dùng cho UI smoke test:** OpenRouter / openai/gpt-4o-mini.

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent hỗ trợ các tình huống IT helpdesk bằng cách chọn tool, lấy dữ liệu từ
nguồn giả lập và trả lời dựa trên kết quả tool. Giao diện Streamlit cho phép
chat nhiều lượt, đồng thời tách riêng phần evidence để quan sát tool calls,
arguments, results/errors, artifact version và transcript.

Giới hạn hiện tại: agent chỉ làm việc trong phạm vi IT service desk và chất
lượng routing phụ thuộc vào phiên bản system_prompt.md và tools.yaml. UI không
tự sửa lỗi routing của model.

**Link dùng thử:**

Chưa có URL deploy công khai. Chạy local từ thư mục starter_v0:

    .\.venv\Scripts\python.exe -m streamlit run app.py

## A2. Tool agent có

UI đọc danh sách tool trực tiếp từ artifacts/tools.yaml, không hard-code tool
registry riêng. Danh sách hiện tại:

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung thông tin hoặc xác nhận | core |
| search_kb | Tìm hướng dẫn trong knowledge base local | core |
| check_service_status | Kiểm tra trạng thái shared service | core |
| inspect_device | Đọc inventory và diagnostic snapshot của asset | core |
| lookup_user | Tra cứu employee và asset được cấp | core |
| format_incident_report | Format findings thành incident report | core |
| policy | Tìm trong chính sách IT nội bộ | optional built-in |
| create_ticket | Tạo ticket sau xác nhận rõ | optional built-in |
| search_device_info | Tìm thông tin thiết bị công khai qua Tavily | optional built-in |

> B cần xác nhận lại tên/schema cuối cùng sau khi hoàn thiện tools.yaml.

## A3. Câu hỏi mẫu

1. Kiểm tra trạng thái VPN production.
2. Kiểm tra tình trạng hardware của thiết bị LT-204.
3. Kiểm tra giúp tôi tình trạng chiếc laptop đang dùng.
4. Sau khi agent hỏi asset ID, trả lời LT-204 để kiểm tra context carry-over.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Shared VPN status | check_service_status với service=vpn, environment=production | UI smoke test trên v0; cần chạy lại bản cuối | transcripts/v0_openrouter_20260914T190218148347.transcript.json (local exploratory) |
| Device hardware lookup | inspect_device với asset_id=LT-204, check=hardware | UI smoke test trên v0; cần chạy lại bản cuối | transcripts/v0_openrouter_20260914T183919067441.transcript.json (local exploratory) |
| Missing asset ID → follow-up LT-204 | Lượt đầu không được tự đoán ID; lượt sau gọi inspect_device với LT-204 | Context carry-over hoạt động; v0 chưa gọi clarify ở lượt đầu | transcripts/v0_openrouter_20260914T183944230763.transcript.json (local exploratory) |

> Các file trong starter_v0/transcripts đang bị .gitignore. Trước khi nộp,
> D phải chạy lại với artifact version cuối và đưa các transcript được chọn vào
> một thư mục evidence được Git track.

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi provider_error_cases == 0, measured_cases == total_cases,
và tool result error đã được review thủ công.

## B1. Version evidence

Phần này chờ A/B cung cấp run files, hypotheses và metric hợp lệ. D chỉ xác nhận
UI hiển thị động version/hash của artifacts và khóa cấu hình trong một phiên
chat để tránh trộn evidence.

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Chờ A/B | Chờ run | — | — | Chờ A/B |
| v1 | Chờ A/B | Chờ A/B | Chờ run | — | — | Chờ A/B |
| v2 | Chờ A/B | Chờ A/B | Chờ run | — | — | Chờ A/B |
| v3 | Chờ A/B | Chờ A/B | Chờ run | — | — | Chờ A/B |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
| UI smoke — missing asset ID | missing_info / boundary | Không có tool call ở lượt đầu | Agent không tự đoán ID và có hỏi lại, nhưng trả lời trực tiếp thay vì gọi clarify | Chuyển evidence cho A để bổ sung global rule; chạy lại trên version cuối |

Các failure khác chờ A/C tổng hợp từ eval runs. D không dùng quan sát UI đơn lẻ
để thay thế automatic evaluation.

## B3. Team eval cases

Chờ C cung cấp đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
| Chờ C | Chờ C | Chờ C | Chưa chạy |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
| VPN production | v0+p233ec2cecfdf+teb3e2243f237 | check_service_status với service=vpn, environment=production | transcripts/v0_openrouter_20260914T190218148347.transcript.json | PASS — 2 rounds, 1 tool call, transcript và download hoạt động |
| Hardware của LT-204 | v0+p233ec2cecfdf+teb3e2243f237 | inspect_device với asset_id=LT-204, check=hardware | transcripts/v0_openrouter_20260914T183919067441.transcript.json | PASS — arguments và tool result hiển thị đúng |
| Thiếu asset ID | v0+p233ec2cecfdf+teb3e2243f237 | Không có tool call | transcripts/v0_openrouter_20260914T183944230763.transcript.json, turn 1 | PARTIAL — không đoán ID nhưng chưa dùng clarify |
| Follow-up LT-204 | v0+p233ec2cecfdf+teb3e2243f237 | inspect_device với asset_id=LT-204, check=all | Cùng transcript, turn 2 | PASS — context carry-over hoạt động |

UI đã được kiểm tra trực tiếp trên máy Windows với Streamlit 1.63.0. Các chức
năng đã xác nhận gồm hai tab Chat/Evidence, quick prompts, reset session, khóa
cấu hình, tool trace, raw model response, lưu transcript và download transcript.

## B4a. Adversarial evidence

Chờ C chạy fixed adversarial suite và cung cấp ít nhất 3 case đã review thủ
công. D sẽ tích hợp evidence vào UI/report sau khi nhận kết quả.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
| Chờ C | Chờ C | Chưa chạy | Chưa kết luận | Chờ evidence |

## B5. Optional và bonus tool evidence

Trong smoke test UI của D chưa chạy create_ticket, policy hoặc
search_device_info; không có ticket được chủ động tạo cho phần test này.
Tavily chưa được cấu hình trong runtime đã test.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in | Chưa có | Chưa test trong phạm vi D hiện tại | Chờ B/A hoàn thiện boundary |
| External search + privacy boundary | Chưa có | Tavily chưa cấu hình | Không được gửi asset ID, employee ID hoặc diagnostics ra ngoài |
| Bonus: tool mới do nhóm tự xây | N/A | D chưa xây bonus tool | N/A |

## B6. Safety review

- Trong missing-info smoke test, agent không tự đoán asset ID; agent hỏi lại và
  dùng LT-204 do người dùng cung cấp ở lượt tiếp theo.
- Các transcript D đã kiểm tra không chứa API key, password, MFA code hoặc token.
- D chưa chạy confirmed-action scenario, vì vậy chưa thể kết luận boundary tạo
  ticket; cần test lại trên version cuối.
- Ba scenario chính không có provider error hoặc tool execution error.
- UI chỉ hiển thị trạng thái key là configured/missing, không hiển thị giá trị key.

## B7. Technical reflection

- D không sửa system_prompt.md; failure không gọi clarify đã được ghi lại để A
  xử lý ở artifact phù hợp.
- D không sửa schema trong tools.yaml; UI tải declarations động để tương thích
  với thay đổi cuối của B.
- Automatic routing score không phản ánh được khả năng đọc của UI, dark-theme
  contrast, download transcript hoặc việc trace có hiển thị đúng result/error.
  Những yếu tố này được kiểm tra trực tiếp trên trình duyệt.
- Quyết định UI quan trọng nhất là tách Chat khỏi Evidence & Debug. Người dùng
  chỉ thấy hội thoại trong tab Chat; giảng viên có thể mở tab Evidence để audit
  tool call, args, result, raw response, version/hash và transcript.
- UI tái sử dụng run_model_tool_loop() từ chat.py, tránh tạo một agent loop riêng
  có thể khác hành vi CLI/eval.
- Mỗi session khóa provider/model/version và cảnh báo khi artifact hash thay đổi,
  giúp transcript không trộn nhiều cấu hình.
- Nếu có thêm một vòng, D sẽ thêm test UI với fake provider để kiểm tra
  deterministic các trạng thái answered, waiting_for_user, provider_error và
  max_tool_rounds, sau đó chạy lại toàn bộ demo trên v3.

# PHẦN C — Checkout trước khi nộp

Phần này chỉ hoàn thành sau khi toàn bộ code, evidence và report được đưa lên
repository chung.

## C1. Reflection chung của nhóm

Chờ cả nhóm thảo luận sau khi A/B/C hoàn thiện artifacts và evidence. D sẽ tổng
hợp reflection chung nhưng không viết thay trải nghiệm hoặc quyết định kỹ thuật
của các thành viên khác.

## C2. Self-reflection của từng thành viên

### Đặng Quốc Cường — MSSV: cần bổ sung

- **Vai trò/phần việc được nhận:** D — UI & Report Coordinator; xây Live Chat
  Streamlit, kiểm thử kịch bản demo và tổng hợp REPORT.md.
- **Những gì tôi đã thay đổi trong repo chung:** Xây giao diện chat nhiều lượt;
  tách Chat và Evidence & Debug; hiển thị tool calls, arguments, results/errors,
  rounds/status, artifact version/hash; lưu và tải transcript; thêm quick prompts,
  reset session và khóa cấu hình trong phiên. Tôi cũng chạy smoke test bằng
  OpenRouter và ghi nhận failure missing-info của baseline v0.
- **File hoặc artifact liên quan:** [app.py](../app.py),
  [requirements.txt](../requirements.txt), artifacts/REPORT.md; transcript
  exploratory trong transcripts sẽ được thay bằng evidence được Git track ở lần
  chạy cuối.
- **Commit hash hoặc pull request:** `83b7655` — `feat(ui): add Streamlit
  helpdesk chat`, branch `D-QuocCuongDang`, Git author
  `D-DangQuocCuong`.
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tôi tái sử dụng
  run_model_tool_loop() và tách giao diện thành hai tab. Cách này giữ hành vi
  nhất quán với CLI trong khi giảm nhiễu cho người dùng bình thường nhưng vẫn
  cung cấp đủ bằng chứng kỹ thuật khi demo.
- **Khó khăn tôi gặp và cách tôi xử lý:** Streamlit dùng dark theme trên máy test,
  làm chữ, JSON và expander thiếu tương phản. Tôi kiểm tra trực tiếp trên trình
  duyệt, bổ sung CSS cho cả dark/light theme và kiểm tra lại từng trạng thái.
  Sticky chat input ban đầu cũng làm trang tự cuộn; tôi chuyển input vào container
  inline để phần đầu trang luôn hiển thị rõ.
- **Điều tôi học được từ phần việc này:** UI của một tool-calling agent phục vụ
  hai nhóm người dùng: người cần câu trả lời và người cần audit quyết định của
  agent. Tách hai luồng hiển thị giúp demo dễ hiểu hơn mà không làm mất evidence.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Tôi sẽ thiết kế fake provider và UI
  smoke tests ngay từ đầu, kiểm tra responsive/accessibility sớm hơn, đồng thời
  thống nhất trước thư mục evidence được commit để tránh transcript cuối bị
  .gitignore.

> A/B/C cần tự bổ sung và commit self-reflection của mình; D không viết thay.

## C3. Final checkout

- [ ] TEAMMATES.md có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [ ] system_prompt.md, tools.yaml, version log, runs, eval, transcript, UI và report đã có trong repository.
- [ ] Transcript demo cuối đã được đưa ra khỏi thư mục bị Git ignore và được link đúng.
- [ ] Không có .env, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng một URL trên VLearn.

**URL repository chung dùng để nộp:**

> Chờ nhóm cung cấp URL cuối.
