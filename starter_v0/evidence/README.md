# Evidence — run và transcript nộp bài

`starter_v0/runs/` và `starter_v0/transcripts/` là thư mục làm việc và bị
gitignore bởi starter. Thư mục này là nơi lưu bản sao đã được review của những
run/transcript dùng làm evidence trong `artifacts/REPORT.md` và
`artifacts/version_log.csv`.

## Cách thêm evidence

1. Chạy eval hoặc chat như bình thường; output rơi vào `runs/` hoặc `transcripts/`.
2. Mở file và kiểm tra trước khi copy:
   - `summary.provider_error_cases == 0`;
   - `summary.measured_cases == summary.total_cases`;
   - không có API key, token, password, MFA/OTP hoặc dữ liệu thật;
   - `tool_results` đã được đọc thủ công, không chỉ nhìn metric.
3. Copy sang đây, giữ nguyên tên file gốc để `version_log.csv` trỏ đúng.

```powershell
Copy-Item runs/<ten_file>.json evidence/runs/
Copy-Item transcripts/<ten_file>.transcript.json evidence/transcripts/
```

## Không đưa vào đây

- run có `provider_error_cases > 0`;
- generated ticket trong `tickets/`;
- `.env`, key, hoặc bất kỳ secret nào.
