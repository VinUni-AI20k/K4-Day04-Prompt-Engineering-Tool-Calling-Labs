# Quy ước Evidence & Quy chuẩn Đặt tên (Shared Evidence Rules)

> **Tài liệu dùng chung cho cả nhóm (Role A, B, C, D, E)**
> **Người thiết lập:** Role C (Eval & Evidence Engineer)
> **Căn cứ:** Issue #2 — Capture v0 baseline and shared evidence rules

---

## 1. Baseline v0 đã thiết lập

Toàn bộ nhóm sử dụng kết quả baseline v0 dưới đây làm mốc so sánh (benchmark) trước khi tối ưu:

- **Provider được chọn:** `openai`
- **Model:** `gpt-4o-mini` (OpenAI provider default)
- **Artifact version:** `v0+p27467914bc4d+t86e19195220e`
  - `prompt_hash`: `27467914bc4d`
  - `tools_hash`: `86e19195220e`
- **Baseline Run File:** `starter_v0/runs/v0_B_base_openai_20260914T192749735306.json`
- **Baseline Metrics (Base Suite - 30 cases):**
  - `total_cases`: 30
  - `measured_cases`: 30 (100%)
  - `provider_error_cases`: **0** *(đạt chuẩn nghiệm thu)*
  - `passed_cases`: 21 / 30
  - `case_accuracy`: **70.0%** (0.7)
  - `tool_routing_accuracy`: 76.67%
  - `argument_accuracy`: 70.0%
  - `multiturn_accuracy`: 80.0% (8/10)

---

## 2. Quy ước đặt tên Version & Trách nhiệm các Role

| Version | Trách nhiệm chính | File thay đổi | Mục tiêu / Giả thuyết |
|---|---|---|---|
| **`v0`** | Role C | Không đổi (starter baseline) | Đo lường hành vi xuất phát trước khi can thiệp. |
| **`v1`** | Role A (Issue #3) | `artifacts/system_prompt.md` | Tối ưu prompt toàn cục, xử lý ngữ cảnh nhiều lượt (multi-turn), ranh giới xác nhận confirmation, không tự đoán thông tin. |
| **`v2`** | Role B (Issue #4) | `artifacts/tools.yaml` | Chuẩn hóa description, tham số, enum enum, boundaries giữa các tool (shared service vs device inspection, v.v.). |
| **`v3`** | Role E & Team (Issue #6, #8) | Cả prompt, tools & guardrails | Hoàn thiện bảo mật, ngăn chặn injection, dữ liệu nhạy cảm, ticket confirmation và bonus tool. |

---

## 3. Quy ước Artifact Version & Hashes

Mỗi phiên bản chạy eval bắt buộc phải đi kèm chuỗi nhận diện duy nhất được tạo tự động bởi `versioning.py`:

$$\text{artifact\_version} = \texttt{v\{N\}+p\{prompt\_hash\}+t\{tools\_hash\}}$$

- `prompt_hash`: SHA256 (12 ký tự đầu) của file `artifacts/system_prompt.md`.
- `tools_hash`: SHA256 (12 ký tự đầu) của file `artifacts/tools.yaml`.
- Khi Role A sửa prompt, `prompt_hash` sẽ tự động đổi.
- Khi Role B sửa tool declarations, `tools_hash` sẽ tự động đổi.

---

## 4. Quy ước Đặt tên và Tiêu chuẩn Chấp nhận Run File

### Cú pháp tên file run:
`run_eval.py` tự động sinh tên file theo định dạng:
```text
starter_v0/runs/{version}_{phase}_{suite}_{provider}_{timestamp}.json
```
*Ví dụ:* `runs/v1_B_base_openai_20260914T190000000000.json`

### Tiêu chuẩn hợp lệ của một Run Evidence:
Một run chỉ được tính là hợp lệ để đưa vào báo cáo khi và chỉ khi:
1. `provider_error_cases == 0`
2. `measured_cases == total_cases` (đo lường đủ 100% số cases của bộ test).
3. Không có ngoại lệ chưa được bắt (unhandled exception).
4. Hash tính lại từ artifact đã commit khớp với `prompt_hash` và `tools_hash` trong run.

---

## 5. Quy ước Đặt tên Transcript (Hội thoại tương tác)

Khi trích xuất hội thoại kiểm thử tương tác (live demo / interactive chat) làm evidence:
```text
starter_v0/transcripts/{kịch_bản}_{version}_{provider}.transcript.json
```
*Ví dụ:*
- `transcripts/vpn_issue_confirm_v1_openai.transcript.json`
- `transcripts/missing_asset_clarify_v2_openai.transcript.json`

Trong file transcript cần lưu rõ:
- `artifact_version`, `prompt_hash`, `tools_hash`
- Danh sách các turns: `user`, `tool_calls`, `tool_results`, `assistant_text`.

---

## 6. Quy ước Cập nhật Nhật ký Phiên bản (`version_log.csv`)

Mỗi khi nhóm hoàn thành một vòng tối ưu và chạy eval thành công, Role phụ trách phiên bản đó phải bổ sung 1 dòng vào `starter_v0/artifacts/version_log.csv` theo định dạng:

```csv
version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_name,metric_before,metric_after,run_file
```

---

## 7. Ranh giới An toàn & Quy tắc Git Commit

1. **Tuyệt đối KHÔNG commit:**
   - File bí mật `.env` hoặc bất kỳ API key / token thật nào.
   - Thư mục `.venv`, `__pycache__`.
   - Các file ticket rác sinh ra trong `starter_v0/tickets/` (khi test `create_ticket`).
   - Run hoặc transcript chưa được review để loại secret và dữ liệu không cần thiết.
   - Chỉ force-add từng evidence file đã được review; không mở theo dõi toàn bộ thư mục generated output.
2. **Quy tắc phối hợp nhánh:**
   - Mỗi thành viên làm việc trên branch riêng của mình: `contrib/<github_username>` (ví dụ: `contrib/thanhnvhust514`).
   - Mở Pull Request vào `main` kèm theo link run evidence tương ứng để nhóm trưởng review và merge.
