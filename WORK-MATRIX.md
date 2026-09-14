# Ma Trận Phân Công Công Việc — Nhóm 5 Người (Zero-Conflict Git Plan)

Tài liệu này xác định phân công công việc chi tiết cho nhóm 5 người thực hiện bài Lab Day 04 ([IT Helpdesk Agent](README.md)). 

Mục tiêu chính:
1. Mỗi thành viên có ít nhất 1 commit riêng được merge vào nhánh chính (`main`).
2. Đảm bảo **100% không bao giờ xảy ra Git merge conflict** nhờ nguyên lý phân lập tệp tin độc lập (**Disjoint-File Isolation**).
3. Đáp ứng đầy đủ các tiêu chí chấm điểm và nộp bài theo [SUBMISSION-GUIDE.md](SUBMISSION-GUIDE.md).

---

## 1. Nguyên Tắc Bất Di Bất Dịch Để Tránh Conflict

- **Nguyên tắc Phân vùng File (Single File Ownership):** Mỗi người chỉ chỉnh sửa và commit đúng các file thuộc phạm vi của mình. Tuyệt đối không chỉnh sửa file của thành viên khác trên branch riêng.
- **Xử lý `REPORT.md` không xung đột:** Cả 5 người cần viết self-reflection, nhưng không cùng mở `REPORT.md` để sửa. Thay vào đó, mỗi người viết vào file riêng trong `starter_v0/artifacts/reflections/member{1..5}.md`. Nhóm trưởng sẽ tổng hợp link vào `REPORT.md` sau khi tất cả đã merge vào `main`.
- **Không bao giờ dùng `git add .`:** Luôn chỉ định rõ đường dẫn file cần commit (ví dụ: `git add starter_v0/artifacts/system_prompt.md`).
- **Không dùng Squash Merge:** Khi merge Pull Request trên GitHub, chỉ dùng **Create a merge commit** hoặc **Rebase and merge** để giữ nguyên commit hash của từng thành viên.

---

## 2. Bảng Ma Trận Phân Công 5 Thành Viên

| TV | Vai trò (Role) | Nhánh Git (Branch) | File ĐỘC QUYỀN phụ trách (Chỉ người này sửa) | Trách nhiệm chính trong Lab | Commit Message mẫu |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **TV 1** | **Nhóm trưởng**<br>*(Lead / DevOps / Baseline)* | `main` & `contrib/tv1-lead` | - `TEAMMATES.md`<br>- `starter_v0/artifacts/version_log.csv`<br>- `starter_v0/artifacts/reflections/member1_lead.md` | - Fork repo, add 4 collaborators.<br>- Tạo `TEAMMATES.md` ở thư mục gốc.<br>- Chạy baseline `v0`, ghi nhận dòng đầu `version_log.csv`.<br>- Review, merge PR của các thành viên và hoàn thiện `REPORT.md`. | `feat(setup): add TEAMMATES.md, init version_log.csv and member1 reflection` |
| **TV 2** | **Prompt Engineer** | `contrib/tv2-prompt` | - `starter_v0/artifacts/system_prompt.md`<br>- `starter_v0/artifacts/reflections/member2_prompt.md` | - Cải thiện prompt ở các version `v1` và `v3`.<br>- Thêm quy tắc: không tự đoán asset/employee ID, xác nhận hành động ghi (`create_ticket`), giữ ngữ cảnh multi-turn. | `feat(prompt): optimize system_prompt rules and add member2 reflection` |
| **TV 3** | **Tool Interface Engineer** | `contrib/tv3-tools` | - `starter_v0/artifacts/tools.yaml`<br>- `starter_v0/artifacts/reflections/member3_tools.md` | - Chuẩn hóa 9 tool declarations trong `tools.yaml` (`v2`).<br>- Tách rõ ranh giới capability (service status vs inspect device, KB vs policy).<br>- Khai báo JSON schema, required args, enum chống hallucinate arguments. | `feat(tools): refine tool schemas, parameters enum and add member3 reflection` |
| **TV 4** | **Evaluation & Test Author** | `contrib/tv4-eval` | - `starter_v0/data/eval_group.json`<br>- `starter_v0/artifacts/reflections/member4_eval.md` | - Thiết kế đúng **10 test cases original** của nhóm (5 single-turn + 5 multi-turn) theo chuẩn lab.<br>- Chạy eval suite trên group dataset để kiểm tra cú pháp và kết quả. | `test(eval): implement 10 team eval test cases and add member4 reflection` |
| **TV 5** | **Security & Demo Specialist** | `contrib/tv5-security` | - `starter_v0/artifacts/adversarial_analysis.md`<br>- `starter_v0/artifacts/transcripts/demo_live_chat.md`<br>- `starter_v0/artifacts/reflections/member5_security.md` | - Chạy bộ `eval_adversarial.json`, phân tích ít nhất 3 security cases (prompt injection, forged state, data exfiltration).<br>- Chạy `python chat.py` test tương tác và trích xuất transcript demo. | `test(security): add adversarial evaluation analysis and chat demo transcript` |

---

## 3. Quy Trình Phối Hợp & Lệnh Git Chi Tiết

### Bước 0: Cấu hình Git Identity (Tất cả 5 người đều phải chạy)
Mở terminal và cấu hình đúng họ tên cùng email GitHub trước khi commit:
```powershell
git config user.name "Họ Và Tên Của Bạn"
git config user.email "email_github_cua_ban@example.com"
```

---

### Thành viên 1 (Nhóm trưởng)
1. Fork repo gốc về GitHub cá nhân: `KX-DAY04-TenNhom`.
2. Mời 4 thành viên vào mục **Settings > Collaborators**.
3. Tạo file `TEAMMATES.md` ở thư mục gốc (đủ họ tên, MSSV, GitHub username, vai trò).
4. Chạy baseline `v0` tại `starter_v0/`:
   ```powershell
   cd starter_v0
   python -m compileall -q .
   python run_eval.py --version v0 --phase B --suite base --provider openrouter
   ```
5. Khởi tạo `starter_v0/artifacts/version_log.csv` và tạo `starter_v0/artifacts/reflections/member1_lead.md`.
6. Commit và push lên `main`:
   ```powershell
   git add TEAMMATES.md starter_v0/artifacts/version_log.csv starter_v0/artifacts/reflections/member1_lead.md
   git commit -m "feat(setup): add TEAMMATES.md, init version_log.csv and member1 reflection"
   git push origin main
   ```

---

### Thành viên 2 (Prompt Engineer)
1. Clone repo và tạo nhánh:
   ```powershell
   git clone <URL_REPO_FORK_CUA_NHOM>
   cd K4A-Day04-GooseGooseDuck
   git switch -c contrib/tv2-prompt
   ```
2. Chỉnh sửa file `starter_v0/artifacts/system_prompt.md`.
3. Viết bản tự nhận xét tại `starter_v0/artifacts/reflections/member2_prompt.md`.
4. Commit và mở Pull Request:
   ```powershell
   git status
   git add starter_v0/artifacts/system_prompt.md starter_v0/artifacts/reflections/member2_prompt.md
   git commit -m "feat(prompt): optimize system_prompt rules and add member2 reflection"
   git push -u origin contrib/tv2-prompt
   ```

---

### Thành viên 3 (Tool Interface Engineer)
1. Clone repo và tạo nhánh:
   ```powershell
   git clone <URL_REPO_FORK_CUA_NHOM>
   cd K4A-Day04-GooseGooseDuck
   git switch -c contrib/tv3-tools
   ```
2. Chỉnh sửa file `starter_v0/artifacts/tools.yaml`.
3. Viết bản tự nhận xét tại `starter_v0/artifacts/reflections/member3_tools.md`.
4. Commit và mở Pull Request:
   ```powershell
   git status
   git add starter_v0/artifacts/tools.yaml starter_v0/artifacts/reflections/member3_tools.md
   git commit -m "feat(tools): refine tool schemas, parameters enum and add member3 reflection"
   git push -u origin contrib/tv3-tools
   ```

---

### Thành viên 4 (Evaluation & Test Author)
1. Clone repo và tạo nhánh:
   ```powershell
   git clone <URL_REPO_FORK_CUA_NHOM>
   cd K4A-Day04-GooseGooseDuck
   git switch -c contrib/tv4-eval
   ```
2. Thiết kế 10 test case trong file `starter_v0/data/eval_group.json`.
3. Viết bản tự nhận xét tại `starter_v0/artifacts/reflections/member4_eval.md`.
4. Commit và mở Pull Request:
   ```powershell
   git status
   git add starter_v0/data/eval_group.json starter_v0/artifacts/reflections/member4_eval.md
   git commit -m "test(eval): implement 10 team eval test cases and add member4 reflection"
   git push -u origin contrib/tv4-eval
   ```

---

### Thành viên 5 (Security & Demo Specialist)
1. Clone repo và tạo nhánh:
   ```powershell
   git clone <URL_REPO_FORK_CUA_NHOM>
   cd K4A-Day04-GooseGooseDuck
   git switch -c contrib/tv5-security
   ```
2. Chạy `eval_adversarial.json`, viết kết quả vào `starter_v0/artifacts/adversarial_analysis.md`.
3. Chạy `python chat.py`, lưu transcript demo vào `starter_v0/artifacts/transcripts/demo_live_chat.md`.
4. Viết bản tự nhận xét tại `starter_v0/artifacts/reflections/member5_security.md`.
5. Commit và mở Pull Request:
   ```powershell
   git status
   git add starter_v0/artifacts/adversarial_analysis.md starter_v0/artifacts/transcripts/demo_live_chat.md starter_v0/artifacts/reflections/member5_security.md
   git commit -m "test(security): add adversarial evaluation analysis and chat demo transcript"
   git push -u origin contrib/tv5-security
   ```

---

## 4. Tích Hợp & Hoàn Thiện Báo Cáo Cuối Cùng

1. **Merge Pull Requests:** Nhóm trưởng duyệt và merge lần lượt 4 Pull Requests trên GitHub (chọn **Create a merge commit** hoặc **Rebase and merge**).
2. **Tổng hợp `REPORT.md`:** 
   Nhóm trưởng kéo code mới nhất về máy:
   ```powershell
   git checkout main
   git pull origin main
   ```
   - Cập nhật số liệu ở các mục A, B trong `starter_v0/artifacts/REPORT.md`.
   - Ở mục **C2. Self-reflection**, dẫn link tới 5 file trong thư mục `starter_v0/artifacts/reflections/`.
   - Commit hoàn tất báo cáo:
     ```powershell
     git add starter_v0/artifacts/REPORT.md
     git commit -m "docs(report): finalize report referencing all member reflections"
     git push origin main
     ```

---

## 5. Checklist Kiểm Tra Cuối Cùng Trước Khi Nộp Bài

Chạy lệnh kiểm tra lịch sử commit trên nhánh `main`:
```powershell
git log --format="%h | %an <%ae> | %s"
```

:::checklist{title="Tiêu chí nghiệm thu bắt buộc" tone="success"}
- [ ] Lịch sử git log có đầy đủ commit riêng của cả 5 thành viên trong nhóm.
- [ ] File `TEAMMATES.md` ở thư mục gốc có đủ thông tin và vai trò của 5 người.
- [ ] Cả 5 file reflection cá nhân nằm trong `starter_v0/artifacts/reflections/`.
- [ ] `system_prompt.md`, `tools.yaml`, `eval_group.json` (đủ 10 cases), `version_log.csv` và `REPORT.md` đã có mặt trên `main`.
- [ ] Không có file nhạy cảm (`.env`, token, cache) bị commit.
- [ ] Cả 5 thành viên đều nộp **cùng 1 link URL fork chung** trên hệ thống VLearn.
:::
