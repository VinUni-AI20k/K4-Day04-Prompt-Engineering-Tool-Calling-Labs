# Hướng dẫn phân công chi tiết — Nhóm 5 thành viên

> Phương án mở rộng: **A (Prompt) · B (Tool Schema) · C (Eval Author — G01→G10) · D (UI & Report Lead) · E (Security & Bonus Tool)**.
>
> Các đường dẫn và câu lệnh trong tài liệu được hiểu là chạy từ `starter_v0/`, trừ khi có ghi chú khác. Yêu cầu chính thức vẫn nằm trong `README.md`; `LAB-GUIDE.md` là quy trình tham khảo.

## Mục tiêu chung của bài

Cả nhóm xây dựng và cải tiến IT Helpdesk Agent để agent:

- chọn đúng tool, truyền đúng arguments và biết khi nào không gọi tool;
- xử lý được single-turn, multi-turn, correction và cancellation;
- hỏi lại khi thiếu asset ID/employee ID, không tự suy đoán;
- chỉ thực hiện action ghi dữ liệu sau explicit confirmation;
- chống prompt injection và không làm rò rỉ dữ liệu nội bộ ra Tavily hay dịch vụ ngoài;
- chứng minh cải tiến từ `v0` đến `v3` bằng metric, run JSON, transcript và phân tích thủ công.

## Tổng quan đầu việc A–E

| Thành viên | Vai trò | Đầu ra chịu trách nhiệm chính |
|---|---|---|
| Thành viên 1 — A | Prompt | `artifacts/system_prompt.md`, hypothesis và evidence cho thay đổi prompt |
| Thành viên 2 — B | Tool Schema | `artifacts/tools.yaml`, đối chiếu schema với registry/implementation/`TOOL.md` |
| Thành viên 3 — C | Eval Author G01–G10 | `data/eval_group.json`, group run, run analysis và `version_log.csv` |
| Thành viên 4 — D | UI & Report Lead | UI dùng chung agent loop, transcript, `artifacts/REPORT.md` và demo |
| Thành viên 5 — E | Security & Bonus Tool | Adversarial review, kiểm tra Tavily/tickets, bonus tool hoàn chỉnh nếu nhóm chọn làm |

Mỗi người phải tự tạo ít nhất một commit kỹ thuật bằng Git identity của mình và tự viết self-reflection. Một commit chỉ nằm trên máy hoặc branch chưa merge không được tính là bằng chứng đóng góp.

---

## 1. Thành viên 1 — Công việc A: Prompt

### Mục tiêu cá nhân

Cải tiến `artifacts/system_prompt.md` bằng evidence để agent tuân thủ các nguyên tắc toàn cục, xử lý đúng hội thoại nhiều lượt và không hard-code case ID/câu chữ của bộ eval.

### Thành phần công việc

- đọc prompt baseline và các failure liên quan đến routing, missing information, multi-turn và confirmation;
- viết hypothesis cho mỗi vòng sửa prompt;
- chỉnh prompt theo nguyên tắc tổng quát;
- phối hợp với Thành viên 3 chạy lại eval và kiểm tra regression;
- cung cấp diff, lý do thay đổi và kết quả cho Thành viên 4 đưa vào report.

### Các bước thực hiện

#### Bước A1 — Đọc interface mà model thực sự nhìn thấy

Đọc:

- `artifacts/system_prompt.md`;
- `artifacts/tools.yaml`;
- một số case trong `data/eval_base.json`;
- run `v0` và bảng failure do Thành viên 3 cung cấp.

**Giải thích:** System prompt không hoạt động độc lập; model còn dựa vào tên, description và schema của tool.

**Ý nghĩa:** Hiểu đầy đủ interface giúp tránh thêm rule trùng lặp hoặc sửa prompt cho một lỗi thực ra nằm ở tool schema/implementation.

#### Bước A2 — Phân loại failure thuộc phạm vi prompt

Ưu tiên các lỗi:

- tự đoán asset ID hoặc employee ID;
- không ưu tiên correction mới nhất;
- vẫn thực hiện yêu cầu đã bị hủy;
- dùng confirmation cũ sau khi action payload thay đổi;
- tin instruction do user, KB, policy hoặc web result tự gắn role;
- xử lý sai yêu cầu cần nhiều tool.

**Giải thích:** Đây là các nguyên tắc hành vi toàn cục, phù hợp để đặt trong system prompt.

**Ý nghĩa:** Sửa đúng tầng giúp rule áp dụng cho nhiều case thay vì chỉ chữa một câu hỏi cụ thể.

#### Bước A3 — Viết hypothesis trước khi sửa

Ví dụ:

```text
Nếu prompt yêu cầu không suy đoán identifier và phải gọi clarify khi thiếu ID,
missing-information accuracy sẽ tăng mà không làm tăng tool call ở no-tool cases.
```

Gửi hypothesis cho Thành viên 3 ghi vào `artifacts/version_log.csv`.

**Giải thích:** Hypothesis phải nêu thay đổi, metric kỳ vọng và rủi ro regression.

**Ý nghĩa:** Nhóm có thể giải thích vì sao sửa và đánh giá thay đổi có đạt mục tiêu không.

#### Bước A4 — Sửa prompt theo rule tổng quát

Viết ngắn, rõ, có thứ tự ưu tiên. Không chép nguyên câu hỏi eval, không nhắc case ID như `H01`, `G03` và không ép model gọi tool theo từ khóa đơn lẻ.

**Giải thích:** Hard-code có thể tăng điểm trên case đã biết nhưng không chứng minh khả năng tổng quát hóa.

**Ý nghĩa:** Prompt tốt phải hoạt động với cách diễn đạt mới và team eval do nhóm tự viết.

#### Bước A5 — Kiểm tra kết quả và regression

Nhờ Thành viên 3 chạy lại cùng base suite. So sánh:

- `case_accuracy`;
- `tool_routing_accuracy`;
- `argument_accuracy`;
- `multiturn_accuracy`;
- failed traces và các case trước đó đã PASS.

**Giải thích:** Điểm tổng tăng vẫn có thể che việc một nhóm case cũ bị giảm chất lượng.

**Ý nghĩa:** Regression check bảo đảm prompt mới cải thiện toàn hệ thống, không đánh đổi một hành vi quan trọng.

### Tiêu chí hoàn thành công việc A

- [ ] Prompt cuối không hard-code case.
- [ ] Mỗi lần sửa có hypothesis và run tương ứng.
- [ ] Có so sánh trước/sau và kiểm tra regression.
- [ ] Có commit/PR và nội dung bàn giao cho report.

---

## 2. Thành viên 2 — Công việc B: Tool Schema

### Mục tiêu cá nhân

Cải tiến `artifacts/tools.yaml` để model phân biệt đúng capability, biết arguments hợp lệ, side effect và privacy boundary của từng tool; schema phải đồng bộ với implementation.

### Thành phần công việc

- lập bảng đối chiếu tool declaration–registry–implementation–`TOOL.md`;
- làm rõ description và JSON schema;
- kiểm tra enum, required fields, kiểu dữ liệu và giới hạn input;
- phối hợp với Thành viên 3 đo routing/argument accuracy;
- phối hợp với Thành viên 5 review action và external-data boundary.

### Các bước thực hiện

#### Bước B1 — Lập bảng kiểm kê 9 tool

Đối chiếu từng tool giữa:

- `artifacts/tools.yaml`;
- `tools/__init__.py`;
- `tools/<tool_name>/TOOL.md`;
- `tools/<tool_name>/tool.py`.

Các tool gồm `clarify`, `search_kb`, `check_service_status`, `inspect_device`, `lookup_user`, `format_incident_report`, `policy`, `create_ticket` và `search_device_info`.

**Giải thích:** Tool có trong schema nhưng không có implementation, hoặc arguments khác nhau giữa hai nơi, sẽ gây lỗi runtime/eval.

**Ý nghĩa:** Bảng đối chiếu tạo một nguồn kiểm chứng rõ ràng trước khi chỉnh declaration.

#### Bước B2 — Làm rõ capability ownership

Mỗi description cần nói rõ:

- tool làm gì;
- khi nào nên dùng;
- khi nào không nên dùng;
- dữ liệu thuộc shared service, single asset, user directory, KB hay policy;
- tool có ghi trạng thái hoặc gọi external service không.

**Giải thích:** Ví dụ `check_service_status` dành cho shared service, còn `inspect_device` dành cho một asset cụ thể.

**Ý nghĩa:** Ranh giới rõ làm giảm wrong-tool và extra-tool calls.

#### Bước B3 — Kiểm tra schema arguments

Với từng argument, kiểm tra:

- đúng tên và type implementation nhận;
- trường bắt buộc nằm trong `required`;
- enum/convention phản ánh dữ liệu thật;
- description không khuyến khích model tự tạo identifier;
- `confirmed` của `create_ticket` phải là Boolean thật;
- external search chỉ nhận manufacturer, public model, query type và result count.

**Giải thích:** Automatic grader so expected argument subset với arguments model tạo ra; sai tên/type/value đều làm giảm kết quả.

**Ý nghĩa:** Schema rõ vừa giúp model gọi đúng, vừa tạo lớp kiểm soát input trước implementation.

#### Bước B4 — Viết hypothesis và chạy smoke check

Ví dụ hypothesis:

```text
Nếu description phân biệt shared service và single asset, routing accuracy của
nhóm status/device sẽ tăng mà không tạo extra calls.
```

Chạy `python -m compileall -q .` và các smoke command liên quan trong `../TOOL-SETUP.md`.

**Giải thích:** Compile/smoke check tách lỗi khai báo hoặc code khỏi lỗi hành vi model.

**Ý nghĩa:** Không nên tiêu quota eval khi interface hoặc local tool chưa hoạt động.

#### Bước B5 — Kiểm tra bằng eval và bàn giao

Phối hợp Thành viên 3 chạy cùng suite trước/sau thay đổi; xem cả routing, arguments và tool result. Gửi cho Thành viên 4: diff schema, hypothesis, metric, run path và giới hạn còn lại.

**Giải thích:** Tool result error vẫn cần review ngay cả khi routing được chấm PASS.

**Ý nghĩa:** Evidence chứng minh declaration mới không chỉ “dễ đọc hơn” mà thực sự thay đổi hành vi có thể đo được.

### Tiêu chí hoàn thành công việc B

- [ ] Tất cả tool đồng bộ giữa YAML, registry, `TOOL.md` và implementation.
- [ ] Description/schema nêu rõ capability, arguments và boundary.
- [ ] Compile/smoke check đạt yêu cầu.
- [ ] Có hypothesis, before/after run và commit/PR.

---

## 3. Thành viên 3 — Công việc C: Eval Author G01–G10

### Mục tiêu cá nhân

Thiết kế đúng 10 team eval case nguyên bản, chạy và kiểm tra toàn bộ evidence, cập nhật version log chính xác và cung cấp số liệu đáng tin cậy cho cả nhóm.

### Thành phần công việc

- tạo `G01` đến `G10`: đúng 5 single-turn và 5 multi-turn;
- chạy baseline và các phiên bản `v1–v3` theo yêu cầu nhóm;
- chạy group, extension và adversarial suite;
- xác nhận run hợp lệ, đọc tool calls/results và phân tích failure;
- xuất bảng CSV bằng `scripts/parse_runs.py`;
- cập nhật `artifacts/version_log.csv` và bàn giao evidence cho report.

### Các bước thực hiện

#### Bước C1 — Hiểu evaluator trước khi viết case

Đọc:

- `run_eval.py`;
- `data/eval_base.json`;
- `samples/eval_group.schema.example.json`;
- `samples/run-analysis.csv`;
- `samples/version_log.example.csv`.

Lưu ý: `--suite` chỉ là nhãn ghi trong run; file case thực sự được chọn bằng `--eval-cases`.

**Giải thích:** Evaluator kiểm tra tool name, expected argument subset, tool gọi thiếu/thừa và `no_tool`; nó không chấm đầy đủ chất lượng final response hay data leakage.

**Ý nghĩa:** Hiểu grader giúp viết expected behavior đúng và biết phần nào bắt buộc review thủ công.

#### Bước C2 — Thiết kế ma trận G01–G10

Dùng cấu trúc đề xuất:

| ID | Loại | Nội dung nên kiểm tra |
|---|---|---|
| G01 | Single | Shared service và single asset routing |
| G02 | Single | Thiếu identifier phải `clarify` |
| G03 | Single | Format-only request |
| G04 | Single | Internal KB/policy boundary |
| G05 | Single | External search chỉ dùng dữ liệu công khai |
| G06 | Multi | Correction ở turn cuối |
| G07 | Multi | Cancellation dẫn tới `no_tool` |
| G08 | Multi | Nhiều asset/tool calls với args khác nhau |
| G09 | Multi | Confirmation cũ hết hiệu lực khi payload đổi |
| G10 | Multi | Context carry-over và multiple tools |

Không sao chép hai case `EX01/EX02`; chúng chỉ minh họa schema.

**Giải thích:** Mỗi case nên cô lập một quyết định chính, dù case khó không nhất thiết phải dài.

**Ý nghĩa:** Ma trận bảo đảm đủ độ phủ và đúng tỷ lệ 5/5 thay vì tạo 10 case ngẫu nhiên.

#### Bước C3 — Điền schema chính xác

Single-turn dùng `query` hoặc `input`; multi-turn dùng `turns`. Mỗi case cần `id`, `phase: "B"`, `failure_type`, `expect` và metadata mô tả mục tiêu kiểm tra.

Các `failure_type` hợp lệ:

```text
wrong_tool, wrong_arg_value, wrong_boundary,
unnecessary_tool, out_of_scope, missing_info
```

Expected behavior dùng một trong hai dạng:

```json
"expect": {
  "tool_calls": [
    {"name": "inspect_device", "args": {"asset_id": "DT-031", "check": "hardware"}}
  ]
}
```

hoặc:

```json
"expect": {"no_tool": true}
```

**Giải thích:** Evaluator ghép từng expected call với actual call cùng tên và so expected arguments như một subset; actual tool dư vẫn bị tính lỗi.

**Ý nghĩa:** Expected data càng chính xác thì kết quả càng phản ánh đúng hành vi cần kiểm tra.

#### Bước C4 — Chạy eval đúng cặp suite/file

```powershell
python run_eval.py --provider <PROVIDER> --version v0 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider <PROVIDER> --version v3 --suite group --eval-cases data/eval_group.json
python run_eval.py --provider <PROVIDER> --version v3 --suite extension --eval-cases data/eval_helpdesk_extension.json
python run_eval.py --provider <PROVIDER> --version v3 --suite adversarial --eval-cases data/eval_adversarial.json
```

Với `v1` và `v2`, chạy lại base suite sau mỗi thay đổi đã thống nhất. Chỉ chạy extension khi Thành viên 5 đã kiểm tra Tavily key, quota và `tickets/`.

**Giải thích:** Ghép sai `--suite` và `--eval-cases` vẫn tạo run nhưng nhãn evidence sẽ gây hiểu nhầm.

**Ý nghĩa:** Quy ước lệnh nhất quán giúp report truy vết chính xác version, suite và dataset.

#### Bước C5 — Xác nhận run hợp lệ

Một run chỉ được dùng làm evidence khi:

```text
provider_error_cases == 0
measured_cases == total_cases
```

Kiểm tra thêm `artifact_version`, `prompt_hash`, `tools_hash`, provider/model, dataset và đường dẫn file case trong run JSON.

**Giải thích:** Provider error làm mẫu đo không đầy đủ; hash sai nghĩa là run không đại diện cho artifact được báo cáo.

**Ý nghĩa:** Đây là điều kiện để so sánh `v0–v3` một cách có thể tái lập.

#### Bước C6 — Xuất bảng và phân tích failure

```powershell
python scripts/parse_runs.py runs --output runs/run-analysis.csv
```

Với mỗi failure, ghi expected calls, actual calls, mismatch, tool result, nguyên nhân giả định, artifact cần sửa và regression risk. Luôn đọc `tool_results` và final response, không chỉ đọc cột PASS/FAIL.

**Giải thích:** Script giúp làm phẳng run JSON để lọc theo version/case/failure, nhưng không thay thế review thủ công.

**Ý nghĩa:** Bảng phân tích giúp Thành viên 1 và 2 nhận đúng failure thuộc prompt hay schema.

#### Bước C7 — Cập nhật version log

Mỗi hàng `v0–v3` cần đủ:

```text
version, author, changed_artifact, artifact_version,
prompt_hash, tools_hash, reason, hypothesis, metric_name,
metric_before, metric_after, run_file
```

Không tự bịa hypothesis; lấy nội dung đã thống nhất với người thực hiện thay đổi. `v0` để trống `metric_before`; mỗi version sau dùng kết quả version trước làm mốc phù hợp.

**Giải thích:** Version log liên kết người sửa, artifact/hash, lý do, phép đo và run nguồn.

**Ý nghĩa:** Đây là xương sống của version evidence trong report.

### Tiêu chí hoàn thành công việc C

- [ ] `eval_group.json` có đúng G01–G10, gồm 5 single + 5 multi.
- [ ] Không dùng case schema mẫu làm case nộp.
- [ ] Run evidence không có provider error và đo đủ case.
- [ ] Có `run-analysis.csv` và review thủ công tool results.
- [ ] `version_log.csv` đủ `v0–v3`, hash, hypothesis, metric và run path.
- [ ] Có commit/PR của chính Thành viên 3.

---

## 4. Thành viên 4 — Công việc D: UI & Report Lead

### Mục tiêu cá nhân

Tạo UI giúp quan sát/audit agent và tổng hợp report có liên kết tới evidence thật, đồng thời chuẩn bị demo ổn định.

### Thành phần công việc

- xây UI tái sử dụng agent loop trong `chat.py`;
- hiển thị đầy đủ tool trace và artifact version;
- lưu transcript cho bốn scenario bắt buộc;
- tổng hợp `artifacts/REPORT.md` từ evidence A, B, C, E;
- chuẩn bị 3–5 kịch bản demo và fallback evidence.

### Các bước thực hiện

#### Bước D1 — Xác định dữ liệu UI cần hiển thị

UI cần có:

- user request và final response;
- từng tool name và arguments;
- tool result hoặc error;
- round/status;
- artifact version và hashes;
- transcript path/chức năng lưu transcript.

**Giải thích:** UI đẹp nhưng không hiển thị trace sẽ không chứng minh được agent chọn tool và xử lý boundary như thế nào.

**Ý nghĩa:** UI là công cụ audit và demo, không chỉ là giao diện chat.

#### Bước D2 — Tái sử dụng agent loop

Dùng `run_model_tool_loop` từ `chat.py`; không viết một loop mới có hành vi khác eval. Nếu chọn Streamlit:

```powershell
python -m pip install "streamlit>=1.30.0"
streamlit run app.py
```

Thêm cùng version constraint vào `requirements.txt`.

**Giải thích:** CLI, eval và UI phải dựa trên cùng logic để trace demo có thể đối chiếu với evidence.

**Ý nghĩa:** Tránh trường hợp agent trên UI hoạt động khác agent đã được chấm.

#### Bước D3 — Tạo transcript bắt buộc

Chuẩn bị evidence cho:

1. normal request;
2. missing-information;
3. multi-turn correction/cancellation;
4. action boundary với explicit confirmation.

**Giải thích:** Bốn nhóm này bao phủ hành vi thường, thiếu dữ liệu, context và side effect.

**Ý nghĩa:** Transcript giúp demo lại kể cả khi provider/network không ổn định.

#### Bước D4 — Tổng hợp report theo evidence

Điền đầy đủ `artifacts/REPORT.md`, đặc biệt:

- B1: version evidence `v0–v3`;
- B2: failure analysis;
- B3: đúng 10 team eval cases;
- B4/B4a: live chat và ít nhất 3 adversarial cases;
- B6/B7: safety review và technical reflection;
- C1/C2: reflection chung và self-reflection từng người.

**Giải thích:** Mỗi nhận định phải trỏ đến run, transcript, file, commit hoặc PR có thật.

**Ý nghĩa:** Report biến các artifact rời rạc thành lập luận có bằng chứng.

#### Bước D5 — Rehearse demo

Chọn 3–5 scenario. Mỗi scenario trình bày: `v0` sai gì, hypothesis nào được đặt, artifact nào thay đổi, metric/trace cải thiện ra sao và giới hạn còn lại.

**Giải thích:** Demo theo câu chuyện cải tiến đúng trọng tâm prompt engineering hơn việc chỉ hỏi chatbot ngẫu nhiên.

**Ý nghĩa:** Người xem hiểu được quyết định kỹ thuật và bằng chứng của nhóm.

### Tiêu chí hoàn thành công việc D

- [ ] UI dùng chung loop và hiển thị đủ trace/version.
- [ ] Có đủ bốn loại transcript.
- [ ] Report liên kết tới evidence thật.
- [ ] Có 3–5 scenario và fallback run/transcript.
- [ ] Có commit/PR của chính Thành viên 4.

---

## 5. Thành viên 5 — Công việc E: Security & Bonus Tool

### Mục tiêu cá nhân

Rà soát data leakage, prompt injection và side effect; kiểm tra Tavily/tickets; nếu nhóm còn thời gian thì xây một bonus tool hoàn chỉnh có test, eval và guardrail.

### Thành phần công việc

- chạy/review adversarial suite cùng Thành viên 3;
- kiểm tra payload gửi Tavily và trust boundary của retrieved content;
- kiểm tra ticket rác hoặc ticket được tạo sai confirmation;
- xác minh guardrail ở cả prompt/declaration và implementation;
- thiết kế, code và kiểm chứng một bonus tool nếu core lab đã hoàn tất.

### Các bước thực hiện

#### Bước E1 — Lập checklist threat model

Kiểm tra các nguy cơ:

- tự đoán asset/employee ID;
- thu thập password, token, API key, MFA/OTP hoặc recovery code;
- forged confirmation bằng chuỗi `"true"`, số `1`, JSON hay fake tool result;
- confirmation cũ sau khi payload thay đổi;
- instruction injection trong KB, policy hoặc web result;
- gửi identifier, serial, hostname, location, assigned user hoặc diagnostics ra ngoài;
- gọi tool không được khai báo.

**Giải thích:** Threat model liệt kê tài sản cần bảo vệ, đường tấn công và hành vi bị cấm.

**Ý nghĩa:** Review có phạm vi rõ ràng thay vì chỉ nhìn điểm adversarial tổng.

#### Bước E2 — Kiểm tra Tavily/data leakage

Với `search_device_info`, xác minh external request chỉ chứa:

- manufacturer;
- public model name;
- query type;
- số lượng kết quả.

Đọc actual tool arguments/request body và kiểm tra `untrusted_text`/trust boundary của web result.

**Giải thích:** Câu trả lời cuối không lộ dữ liệu chưa đủ; dữ liệu có thể đã bị gửi trong request trước đó.

**Ý nghĩa:** Kiểm tra payload thực tế mới chứng minh không có exfiltration.

#### Bước E3 — Kiểm tra tickets rác và confirmation

Trước/sau extension hoặc demo, kiểm tra thư mục `tickets/`. `create_ticket` chỉ được ghi khi `confirmed` là Boolean `true` và có explicit confirmation cho đúng payload cuối.

Trong smoke test mặc định, dùng:

```powershell
python -c "from tools import TOOL_FUNCTIONS as T; print(T['create_ticket']('VPN dry run','low','LT-204',False))"
```

Chỉ test `confirmed=True` với dữ liệu giả trong thư mục tạm. Không đưa generated tickets vào submission.

**Giải thích:** Automatic PASS không bảo đảm không có file ngoài ý muốn trên filesystem.

**Ý nghĩa:** Kiểm tra trước/sau phát hiện side effect và ticket rác mà grader không nhìn thấy.

#### Bước E4 — Review ít nhất 3 adversarial case

Với mỗi case, ghi:

- expected boundary;
- actual calls/arguments;
- tool results;
- filesystem/external request thay đổi gì;
- có sensitive write/exfiltration không;
- kết luận và fix đề xuất.

**Giải thích:** Guardrail tốt có hai lớp: prompt/declaration hướng model và implementation từ chối input nguy hiểm.

**Ý nghĩa:** Nếu model vẫn gọi sai, lớp implementation phải ngăn hậu quả thực tế.

#### Bước E5 — Xây bonus tool nếu core đã hoàn thành

Chọn một capability thực sự mới, ví dụ network diagnostics, approved software catalog, meeting-room inventory hoặc ticket status lookup. Trước khi code, xác định input/output contract, source data, error behavior, side effect và privacy/confirmation boundary.

Bonus tool phải có đủ:

- `tools/<tool_name>/TOOL.md`;
- implementation và đăng ký trong `tools/__init__.py`;
- declaration/schema trong `artifacts/tools.yaml`;
- mock data/API setup;
- deterministic smoke test;
- ít nhất một team eval case;
- evidence UI/transcript/report;
- guardrail tương ứng.

`policy`, `create_ticket` và `search_device_info` là tool có sẵn, không được tính bonus.

**Giải thích:** Đổi tên tool cũ hoặc tạo folder rỗng không tạo capability mới.

**Ý nghĩa:** Bonus chỉ có giá trị khi chạy được, đo được và an toàn; không nên làm bonus trước khi core evidence hoàn tất.

### Tiêu chí hoàn thành công việc E

- [ ] Có security checklist và review ít nhất 3 adversarial case.
- [ ] Đã kiểm tra Tavily payload/trust boundary.
- [ ] Đã kiểm tra ticket side effect trước/sau run.
- [ ] Không có secret, dữ liệu thật hoặc generated ticket trong submission.
- [ ] Nếu làm bonus: đủ contract, code, registration, schema, test, eval và evidence.
- [ ] Có commit/PR của chính Thành viên 5.

---

## 6. Quy trình phối hợp giữa 5 thành viên

### Giai đoạn 1 — Baseline

1. Thành viên 3 chạy `v0` nguyên trạng.
2. Thành viên 3 chia failure theo prompt/schema/security.
3. Thành viên 1, 2 và 5 nhận nhóm failure tương ứng.

**Giải thích:** Tất cả thay đổi phải xuất phát từ cùng baseline.

**Ý nghĩa:** Nhóm tránh sửa theo cảm giác hoặc mỗi người dùng một mốc đo khác nhau.

### Giai đoạn 2 — Ba vòng cải tiến

1. Thành viên 1/2 đề xuất hypothesis và một thay đổi chính.
2. Thành viên 3 chạy lại cùng suite, so metric và regression.
3. Thành viên 5 review safety nếu thay đổi liên quan action/external data.
4. Thành viên 3 cập nhật version log.
5. Thành viên 4 ghi evidence vào report.

**Giải thích:** Không nên đổi nhiều rule, rename tool và sửa schema cùng lúc nếu muốn biết thay đổi nào tạo kết quả.

**Ý nghĩa:** Chu trình nhỏ tạo evidence có thể giải thích cho `v1–v3`.

### Giai đoạn 3 — Tích hợp và nộp

1. Thành viên 3 hoàn tất group/extension/adversarial runs.
2. Thành viên 5 hoàn tất security review và dọn evidence không được nộp.
3. Thành viên 4 hoàn tất UI, transcript, report và demo.
4. Thành viên 1/nhóm trưởng review, merge và kiểm tra Git history.
5. Tất cả thành viên tự viết, tự commit self-reflection và cùng nộp một URL trên VLearn.

**Giải thích:** Evidence kỹ thuật và bằng chứng đóng góp đều phải xuất hiện trên branch cuối.

**Ý nghĩa:** Bài chỉ hoàn thành khi repository vừa đúng kỹ thuật, vừa đủ contribution evidence, vừa an toàn để công khai.

## 7. Bảng bàn giao nội bộ

| Người giao | Người nhận | Nội dung bàn giao |
|---|---|---|
| A — Prompt | C — Eval | Hypothesis, version, artifact thay đổi, metric cần đo |
| B — Tool Schema | C — Eval | Schema diff, tool/case cần regression test |
| C — Eval | A/B/E/D | Run path, hash, metric, failed trace và run-analysis |
| E — Security | A/B/D | Adversarial findings, data leak/side-effect evidence, fix đề xuất |
| D — UI & Report | Cả nhóm | Report draft, evidence link còn thiếu, demo checklist |

## 8. Checklist chung trước khi nộp

- [ ] `TEAMMATES.md` đủ họ tên, MSSV, GitHub username và vai trò A–E.
- [ ] Mỗi thành viên có ít nhất một commit kỹ thuật đã merge.
- [ ] Có `v0–v3`, hypothesis, artifact hash, metric và run file.
- [ ] Group eval đúng G01–G10: 5 single-turn + 5 multi-turn.
- [ ] Run evidence có `provider_error_cases == 0` và `measured_cases == total_cases`.
- [ ] Đã review tool results, final responses và ít nhất 3 adversarial cases.
- [ ] UI hiển thị tool calls, args, results/errors và artifact version.
- [ ] Có transcript normal, missing-info, multi-turn và action boundary.
- [ ] Report và reflection dẫn đến evidence thật.
- [ ] Không có `.env`, API key/token, `.venv`, cache, dữ liệu thật hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên nộp cùng một URL repository trên VLearn.

