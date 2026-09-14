# UI Demo Report - IT Helpdesk Agent

Tài liệu này dùng cho phần thuyết trình demo qua giao diện chat của Người 4 - UI.
Mục tiêu là trình bày ngắn gọn UI đã tích hợp những gì, đáp ứng requirement nào, và demo end-to-end như thế nào.

## 1. Vai trò của UI trong bài lab

UI không thay thế evaluator, mà dùng để demo trực quan cách agent hoạt động trong một phiên chat thật.
Giao diện giúp người xem thấy được:

- Người dùng nhập yêu cầu helpdesk.
- Agent trả lời bằng nội dung dễ đọc.
- Agent gọi tool nào.
- Tool nhận arguments gì.
- Tool trả result/error gì.
- Transcript được ghi lại để làm evidence.

## 2. Các phần đã hoàn thành

| Requirement | Trạng thái | Evidence/file |
|---|---|---|
| Có giao diện chat hoạt động | Hoàn thành | `starter_v0/app.py` |
| UI dùng chung agent loop có sẵn | Hoàn thành | `run_model_tool_loop` trong `starter_v0/chat.py` |
| Load system prompt từ artifact | Hoàn thành | `starter_v0/artifacts/system_prompt.md` |
| Load tool schema từ artifact | Hoàn thành | `starter_v0/artifacts/tools.yaml` |
| Tích hợp provider setup | Hoàn thành | Sidebar trong `starter_v0/app.py` |
| Đọc `.env` ở root repo và `starter_v0/.env` | Hoàn thành | `starter_v0/env_loader.py` |
| Hỗ trợ alias `ENV_OPENAI -> OPENAI_API_KEY` | Hoàn thành | `starter_v0/env_loader.py` |
| Hiển thị tool calls | Hoàn thành | Tool trace trong UI |
| Hiển thị tool arguments | Hoàn thành | Tool trace trong UI |
| Hiển thị tool result/error | Hoàn thành | Tool trace trong UI |
| Lưu transcript demo | Hoàn thành | `starter_v0/transcripts/*.transcript.json` |
| Chat chỉ hiển thị nội dung người dùng cần đọc | Hoàn thành | UI parse JSON và chỉ show field `reply` |
| Tool trace không tự mở | Hoàn thành | Round trace chỉ mở khi click |
| Sidebar gọn, đúng trọng tâm demo | Hoàn thành | Provider + New chat + Advanced settings |

## 3. Các file đã chỉnh sửa/thêm

| File | Nội dung đã làm |
|---|---|
| `starter_v0/app.py` | Thêm Streamlit UI cho chat, provider config, tool trace và transcript |
| `starter_v0/env_loader.py` | Cho phép đọc `.env` từ root repo, hỗ trợ alias biến môi trường |
| `starter_v0/requirements.txt` | Thêm dependency `streamlit>=1.30.0` |
| `TEAM_WORK_SPLIT_5.md` | Cập nhật workflow Người 4 - UI |

## 4. Cách chạy UI

Chạy từ thư mục `starter_v0`:

```powershell
cd starter_v0
python -m streamlit run app.py
```

Nếu máy đã có command `streamlit` trong PATH, có thể chạy:

```powershell
streamlit run app.py
```

Sau khi chạy, mở URL local mà Streamlit in ra, ví dụ:

```text
http://localhost:8501
```

## 5. Cấu hình provider

UI cho phép chọn provider trong sidebar:

- `openai`
- `openrouter`
- `anthropic`
- `gemini`

Trong demo hiện tại, provider nên chọn `openai` nếu file `.env` ở root đang dùng biến:

```text
ENV_OPENAI=...
```

Code đã tự map biến này sang:

```text
OPENAI_API_KEY
```

Không hiển thị API key trên UI và không commit `.env`.

## 6. Thiết kế UI sau khi tinh gọn

UI được tinh gọn để tập trung vào người dùng:

- Sidebar chỉ giữ cấu hình cần thiết.
- Các cấu hình kỹ thuật đưa vào `Advanced settings`.
- Màn hình chính chỉ có `Chat` và `Tool trace`.
- Không hiển thị path transcript dài, artifact preview, run evidence hoặc key status trên màn hình demo.
- Tool trace mặc định đóng, chỉ mở khi người thuyết trình click vào.

## 7. Luồng xử lý end-to-end

Khi người dùng gửi message:

1. UI đọc `system_prompt.md`.
2. UI đọc `tools.yaml`.
3. UI tạo provider tương ứng.
4. UI gọi `run_model_tool_loop` từ `chat.py`.
5. Agent quyết định có gọi tool hay không.
6. Tool local được execute.
7. Agent tạo final response.
8. UI hiển thị nội dung `reply` cho người dùng.
9. UI hiển thị tool trace nếu có tool call.
10. UI ghi transcript JSON vào `starter_v0/transcripts/`.

## 8. Kịch bản demo đề xuất

### Demo 1 - Hỏi chính sách IT

Prompt:

```text
Account Access and Identity Verification Policy
```

Điều cần cho người xem thấy:

- Agent route sang policy knowledge.
- UI chỉ hiển thị text trả lời chính sách, không show raw JSON.
- Tool trace có thể mở ra để xem tool call và result.

Expected behavior:

- Có tool call `policy`.
- Response giải thích chính sách account access/identity verification.
- Có evidence từ policy source.

### Demo 2 - Kiểm tra shared service

Prompt:

```text
Dịch vụ VPN production hiện có đang gặp sự cố không?
```

Điều cần cho người xem thấy:

- Agent phân biệt shared service với thiết bị cá nhân.
- Tool trace gọi `check_service_status`.
- Arguments gồm `service=vpn`, `environment=production`.

Expected behavior:

- Không gọi `inspect_device`.
- Có status/result từ mock service data.

### Demo 3 - Thiếu asset ID

Prompt:

```text
Kiểm tra Wi-Fi trên laptop của mình giúp nhé.
```

Điều cần cho người xem thấy:

- Agent không đoán asset ID.
- Agent gọi `clarify`.
- UI hiển thị câu hỏi yêu cầu người dùng bổ sung mã asset.

Expected behavior:

- Tool call `clarify`.
- `response_type=text`.

### Demo 4 - Multi-tool triage

Prompt:

```text
VPN trên LT-204 lỗi; kiểm tra cả trạng thái VPN production và máy đó.
```

Điều cần cho người xem thấy:

- Một request có thể cần nhiều tool.
- Tool trace có `check_service_status` và `inspect_device`.
- Arguments rõ ràng cho từng tool.

Expected behavior:

- `check_service_status(service=vpn, environment=production)`.
- `inspect_device(asset_id=LT-204, check=vpn)`.

### Demo 5 - Ticket confirmation boundary

Prompt:

```text
Tạo ticket mức high cho lỗi VPN trên LT-204 giúp mình.
```

Điều cần cho người xem thấy:

- Agent không tạo ticket ngay.
- Agent hỏi xác nhận trước.
- Tool trace gọi `clarify` với `response_type=yes_no`.

Expected behavior:

- Không gọi `create_ticket` khi chưa có xác nhận rõ.
- Có câu hỏi xác nhận payload ticket.

## 9. Script thuyết trình ngắn

Có thể trình bày như sau:

```text
Phần UI được xây bằng Streamlit trong file starter_v0/app.py.
UI không viết lại agent loop mà dùng lại run_model_tool_loop trong chat.py,
vì vậy behavior giữa CLI, eval và UI là nhất quán.

Khi người dùng nhập yêu cầu, UI load system_prompt.md và tools.yaml hiện tại,
sau đó gửi vào provider đã chọn. Nếu model gọi tool, UI hiển thị tool trace gồm
tên tool, arguments và result. Final answer trong chat được làm sạch để người dùng
chỉ thấy nội dung reply thay vì raw JSON.

UI cũng ghi transcript vào starter_v0/transcripts để nhóm dùng làm evidence trong report.
Các phần kỹ thuật như model override, history window và artifact path được đưa vào
Advanced settings để giao diện demo gọn và đúng trọng tâm người dùng.
```

## 10. Lưu ý khi demo

- Không mở hoặc show `.env`.
- Không show API key.
- Không commit transcript nếu `.gitignore` đang ignore `starter_v0/transcripts/`.
- Nếu provider lỗi, kiểm tra package và key:

```powershell
python -m pip install -r requirements.txt
python scripts/preflight_provider.py --provider openai
```

- Nếu command `streamlit` không chạy trên Windows, dùng:

```powershell
python -m streamlit run app.py
```

## 11. Phần đã đáp ứng trong requirement UI

Theo README, UI cần chat hoạt động và hiển thị được tool calls, args, result/error, artifact version/transcript evidence.
Hiện UI đã đáp ứng các phần trọng tâm:

- Chat hoạt động.
- Tool trace có tool name.
- Tool trace có args.
- Tool trace có result/error.
- Transcript được tạo tự động.
- Artifact vẫn được load từ file thật.

Phần artifact version/hash không hiển thị trực tiếp trên màn hình chính vì đã tinh gọn UI theo hướng demo người dùng.
Thông tin này vẫn được ghi trong transcript JSON thông qua `artifact_version_dict`.

