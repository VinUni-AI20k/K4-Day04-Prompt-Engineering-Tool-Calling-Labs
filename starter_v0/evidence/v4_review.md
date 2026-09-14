# v4 — environment enum boundary (tools.yaml)

- Runs: `evidence/runs/v4_B_base_openai_20260914T194029251592.json`,
  `evidence/runs/v4_B_extension_openai_20260914T194050842871.json`
- Artifact version: `v4+p60242d8c7b9b+t6b18de0c4bdb`
- Provider/model: `openai` / `gpt-4o-mini`

## Bối cảnh

Sau v3, H19 vẫn FAIL và đã được ghi là giới hạn. Rủi ro khi sửa: luật clarify
quá rộng từng làm vỡ H02 ở v3, nên siết thêm có thể làm vỡ H06, M02, H15 — ba
case đang PASS nhờ xác định environment hợp lệ.

Trước khi sửa, đã đọc lại cách diễn đạt của cả bốn case environment:

| Case | User nói | Kỳ vọng |
|---|---|---|
| H06 | "Email **staging** đang hoạt động bình thường chứ?" | `environment: staging` |
| M02 | turn3 "Chỉ kiểm tra email, vẫn là **staging**." | `environment: staging` |
| H15 | "So sánh **production** và **staging**" | hai call |
| H19 | "môi trường **demo** của team QA" | `clarify` choice |

Ranh giới sạch hơn dự đoán: ba case PASS đều gọi **đúng tên** `production` hoặc
`staging`; chỉ H19 dùng một từ không có trong enum. Luật bám vào đúng điểm đó
nên rủi ro thấp hơn nhiều so với một luật clarify toàn cục.

## Thay đổi

Chỉ `check_service_status.environment` trong `tools.yaml`. Mô tả cũ nói "chỉ
dùng 'staging' khi người dùng chỉ định rõ" — không đủ, vì model coi "demo" là
một cách chỉ định. Mô tả mới liệt kê thẳng những tên **không** tương ứng với môi
trường nào — demo, test, dev, QA, UAT, sandbox, staging của một team riêng — và
yêu cầu hỏi lại bằng `clarify` với `response_type: choice`.

`system_prompt.md` không đổi: `prompt_hash` giữ nguyên `60242d8c7b9b` từ v3, chỉ
`tools_hash` đổi `abdbd9b3e355` → `6b18de0c4bdb`.

## Kết quả

| Metric | v0 | v1 | v2 | v3 | **v4** |
|---|---:|---:|---:|---:|---:|
| case_accuracy (base) | 0.70 | 0.80 | 0.90 | 0.9333 | **1.00** |
| tool_routing_accuracy | 0.7667 | 0.8333 | 0.9667 | 0.9667 | **1.00** |
| argument_accuracy | 0.70 | 0.80 | 0.90 | 0.9333 | **1.00** |
| multiturn_accuracy | 0.80 | 0.80 | 1.00 | 1.00 | **1.00** |
| case_accuracy (extension) | — | — | 0.60 | 1.00 | **1.00** |

Base **30/30**, extension **10/10**, `provider_error_cases = 0` ở cả hai.

**Không có regression.** H06, M02, H15 đều PASS và vẫn dùng đúng `staging` /
`production`. H19 giờ gọi:

```json
clarify {"question": "Môi trường bạn muốn kiểm tra có phải là 'production' hay
'staging'?", "response_type": "choice", "options": ["production", "staging"]}
```

H11 cũng PASS theo, lần này có `response_type: "text"` — cùng một prompt, cùng
một case, khác kết quả so với v3. Điều này xác nhận nhận định ở v3: H11 không
thiếu luật mà là model không nhất quán. Không nên coi một lần PASS là bằng chứng
đã sửa xong.

## Bằng chứng an toàn

`create_ticket` chỉ được gọi ở E05 và E08, cả hai `confirmed=true` hợp lệ. Base
suite 30 case: **0 ticket trái phép**. `tickets/` đã dọn sau khi kiểm tra.

## Tool result cần review thủ công

Metric 1.00 không có nghĩa mọi tool đều chạy đúng. Probe `tool_results` của cả
hai suite phát hiện hai nhóm vấn đề, cả hai đều **PASS** trong bảng điểm:

### `search_device_info` trả `missing_api_key` — E09, E10

Chưa cấu hình `TAVILY_API_KEY`. Evaluator chỉ chấm tool nào được gọi với
argument gì, không chấm tool có chạy được không, nên hai case này PASS dù tool
thất bại hoàn toàn.

Routing và argument boundary vẫn đúng — E10 gọi `inspect_device` cho dữ liệu nội
bộ và `search_device_info` chỉ với manufacturer/model công khai. Nhưng muốn dùng
làm evidence cho phần external search thì phải chạy lại sau khi có Tavily key.

### `policy` trả kết quả rỗng — E02, E03, E06

`policy_area` chọn **đúng** ở cả ba, nhưng `results: 0`:

| Case | args | results |
|---|---|---:|
| E01 | `query="mã MFA"`, `access_control` | 2 |
| E04 | `query="tạo ticket"`, `ticketing` | 2 |
| E02 | `query="password, token"`, `data_privacy` | **0** |
| E03 | `query="sự cố toàn công ty"`, `incident_response` | **0** |
| E06 | `query="thay đổi cấu hình dịch vụ"`, `service_operations` | **0** |

Đã kiểm chứng trực tiếp bằng cách gọi tool với query tiếng Anh:

```
policy("password token", "data_privacy")   -> 0 results
policy("restricted data", "data_privacy")  -> 2 results
policy("priority", "incident_response")    -> 1 result
```

Nguyên nhân: văn bản trong `company_policy/` viết bằng tiếng Anh, còn `policy`
khớp theo từ khóa chứ không hiểu ngữ nghĩa. Query tiếng Việt không khớp được.
E01 và E04 có kết quả vì "MFA" và "ticket" là từ trùng nhau ở hai ngôn ngữ.

Đây là **giới hạn của implementation**, không phải lỗi định tuyến của nhóm.
LAB-GUIDE mục 5 nói rõ không nên dùng prompt để che một lỗi thuộc implementation,
nên không sửa bằng cách ép model dịch query sang tiếng Anh — việc đó sẽ làm đẹp
số mà giấu đi vấn đề thật.

Cần ghi vào REPORT.md mục B6: ba case này PASS nhưng agent không thực sự đọc
được nội dung policy nào để trả lời.

## Đánh giá

Việc H19 sửa được cho thấy nhận định "đây là giới hạn" ở v3 là **chưa đủ sâu**.
Vấn đề không phải model không chịu hỏi lại, mà là nó không có tín hiệu nào để
biết "demo" là một từ nằm ngoài enum. Luật toàn cục trong prompt quá xa ngữ cảnh
để tạo ra tín hiệu đó; một dòng mô tả ngay tại chỗ khai báo argument thì đủ.

Đây cũng là ví dụ rõ cho câu hỏi prompt vs schema: cùng một hành vi mong muốn
(hỏi lại khi giá trị không hợp lệ), viết ở prompt thì hỏng H02, viết ở
declaration thì không hỏng gì.
