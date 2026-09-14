# Prompt cho C — Eval & Red-Team (keilelser-05)

> Copy toàn bộ phần dưới vào coding agent, mở tại thư mục gốc của repo chung.

---

Bạn là coding agent hỗ trợ tôi (GitHub `keilelser-05`, vai trò **C — Eval & Red-Team**) trong bài lab nhóm "Day 04 — IT Helpdesk Agent". Repo: `https://github.com/pbaodev/K4-Day04-2A202602767`. Làm việc trong `starter_v0/`.

## Bối cảnh bắt buộc đọc trước
1. `README.md` (mục "Bộ eval hiện tại", "Ranh giới an toàn"), `LAB-GUIDE.md` mục 7–8, `docs/team-prompts/README.md`.
2. `starter_v0/run_eval.py` — cách chấm: tool name, subset args, missing/extra calls, `no_tool`; multi-turn chỉ chấm **turn cuối**; eval gọi model **một lần** nên mọi tool cần thiết phải nằm trong cùng response.
3. `starter_v0/samples/eval_group.schema.example.json` — format case (2 case mẫu **không được tính**).
4. `starter_v0/data/eval_base.json`, `eval_helpdesk_extension.json`, `eval_adversarial.json` — để **tránh trùng** ý tưởng/wording.
5. Mock data: `starter_v0/helpdesk_data/assets.json`, `users.json`, `service_status.json`, `knowledge_base/`, `company_policy/` — mọi ID trong case phải tồn tại (hoặc cố ý không tồn tại, có ghi rõ).
6. Tool declarations `starter_v0/artifacts/tools.yaml` và run evidence trong `starter_v0/runs/`.

## Setup
```bash
git pull origin main
git switch -c contrib/keilelser-05
cd starter_v0
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
```
Tôi tự điền `GROQ_API_KEY=...` và `GROQ_MODEL=qwen/qwen3.8-27b` trong `.env` (key free tại https://console.groq.com/keys). Agent không đọc/in/commit giá trị key.
Kiểm tra: `python scripts/preflight_provider.py --provider groq`.

## Nhiệm vụ

### 1. Viết `data/eval_group.json` — đúng 10 case original
- IDs `G01`…`G10` (dạng `G01_<ten_ngan>`), `phase: "B"`, **G01–G05 single-turn** (`query`), **G06–G10 multi-turn** (`turns`, ≥ 3 lượt user).
- `failure_type` chỉ dùng: `wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`.
- `expect` chỉ dùng `tool_calls` (name + subset args chắc chắn đúng) hoặc `no_tool: true` + `behavior`. Không đưa arg mơ hồ (ví dụ `query` tự do) vào expected args.
- `metadata.what_it_tests` 1 câu; thêm `metadata.skill`, `metadata.difficulty`.
- Mỗi case **cô lập một quyết định**, tiếng Việt tự nhiên, không copy/biến thể nhẹ của case có sẵn. Gợi ý bao phủ:
  - ambiguous intent / identifier thiếu (clarify `text`);
  - giá trị ngoài enum (clarify `choice` + `options`);
  - hai call cùng tool khác args (ví dụ 2 service hoặc 2 asset);
  - correction ở turn sau; cancellation; latest intent wins;
  - stale confirmation khi payload đổi (clarify `yes_no`);
  - confirmation hợp lệ sau revision (create_ticket `confirmed: true` với payload mới);
  - format-only không refetch;
  - external/internal boundary cho `search_device_info` (không lẫn asset/employee ID);
  - nếu E làm bonus tool: 1 case cho tool đó (phối hợp với DuyBach2003, chỉ thêm khi tool đã merge).
- Validate cú pháp và đếm: `python -c "import json;c=json.load(open('data/eval_group.json'))['cases'];print(len(c), sum('turns' in x for x in c))"` → phải là `10 5`.

### 2. Chạy group suite
```bash
python run_eval.py --provider groq --version <version hiện tại trên main> --suite group --eval-cases data/eval_group.json
```
- Lần đầu dùng để kiểm tra case có chấm được không. Nếu một case fail vì **expected sai** (không phải agent sai) thì sửa case, và ghi lý do.
- **Không** chỉnh expected để "làm cho pass" khi agent thực sự sai — đó là finding cần báo lead.
- Sau khi lead merge **v3**: chạy lại với `--version v3` làm evidence chính thức. Run hợp lệ khi `provider_error_cases == 0` và `measured_cases == 10`.

### 3. Adversarial suite + phân tích thủ công
- Đã có run `v0` (và `v1`) adversarial trong `runs/`. Sau khi có v3, chạy:
  ```bash
  ls tickets/ 2>/dev/null   # ghi lại trạng thái trước
  python run_eval.py --provider groq --version v3 --suite adversarial --eval-cases data/eval_adversarial.json
  ls tickets/ 2>/dev/null   # so sánh sau
  ```
- Phân tích **ít nhất 3 case** (khuyến nghị: A04 argument smuggling, A10 stale confirmation, A12 external identifier smuggling, A01 prompt exfiltration). Với mỗi case so sánh v0 → v3:
  - tool nào **thực sự** được gọi, args gì (`result.actual_tool_calls`);
  - `tool_results`: có ticket được tạo không (có `ticket_id`/file mới trong `tickets/`?), `search_device_info` có nhận identifier nội bộ không, implementation có chặn không;
  - final text có lộ system prompt/schema không;
  - PASS tự động có thật sự an toàn không.
- Viết kết quả thành bảng đúng cột của REPORT mục **B4a**: `Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome`.
- Sau khi phân tích, xoá `tickets/*.json` (không commit ticket).

### 4. Commit & PR
- Commit: `data/eval_group.json`, run group v3 + adversarial v3 hợp lệ trong `runs/`, file phân tích `docs/adversarial-analysis.md` (bảng B4a + ghi chú v0→v3).
- Commit message ví dụ `test(eval): add 10 original group cases G01-G10`, `docs(redteam): adversarial analysis v0 vs v3` — commit bằng Git identity của tôi.
- Push `contrib/keilelser-05`, mở PR vào `main`, mô tả: bảng 10 case (ID, what it tests, expected, result), metric group, tóm tắt adversarial.

### 5. Góp nội dung REPORT (gửi D tổng hợp)
- B3 (bảng 10 case), B4a (≥ 3 attack case), B7 "Failure nào không thể chỉ nhìn automatic score?".

## Ràng buộc
- Không sửa eval base/extension/adversarial, không sửa `system_prompt.md`/`tools.yaml`.
- Không dùng dữ liệu thật, password/token thật trong case (chỉ chuỗi giả rõ ràng).
- Không commit `.env`, key, `.venv`, `tickets/`.
- Không tự viết self-reflection C2 — tôi tự viết.
- Khi không chắc expected behavior đúng là gì, đọc README "Ranh giới an toàn" rồi hỏi tôi.

## Definition of done
- [ ] `eval_group.json` đúng 10 case (5 single + 5 multi), load được bởi `run_eval.py`.
- [ ] Run group v3 hợp lệ.
- [ ] Run adversarial v3 hợp lệ + phân tích ≥ 3 case có kiểm tra `tool_results` và `tickets/`.
- [ ] PR mở vào `main` với commit của `keilelser-05`.
