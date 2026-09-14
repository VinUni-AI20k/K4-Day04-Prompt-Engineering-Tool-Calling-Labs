# Quy trình làm việc nhóm

## Phân vai

| Role | Phụ trách | Issue |
|---|---|---|
| Nhóm trưởng, D | UI, tích hợp, review, demo và report | #7, #8 |
| A | System prompt và hội thoại nhiều lượt | #3 |
| B | Tool descriptions, schemas và smoke tests | #4 |
| C | Baseline, G01-G10, eval và version evidence | #2, #5 |
| E | Security, Tavily, ticket safety và bonus tool | #6 |

## Thứ tự thực hiện

1. C hoàn thành baseline #2 trước.
2. Sau #2, A làm #3, B làm #4, E làm #6 và nhóm trưởng làm #7 song song.
3. Khi #3 và #4 hoàn thành, C thực hiện team eval #5.
4. Nhóm trưởng chỉ bắt đầu tích hợp cuối #8 khi #3 đến #7 đã hoàn thành.

## Quy trình cho mỗi thành viên

1. Đọc đầy đủ issue được giao và nhận việc bằng comment.
2. Tạo branch riêng từ `main` mới nhất.
3. Thực hiện một phạm vi nhỏ đúng acceptance criteria.
4. Chạy test, smoke check hoặc eval liên quan.
5. Mở pull request và dẫn link evidence.
6. Sửa review feedback rồi chờ nhóm trưởng merge.
7. Tự viết và commit phần self-reflection của mình.

Tên branch đề xuất:

```text
A: feature/prompt-v1
B: feature/tool-contracts-v2
C: feature/eval-evidence
E: feature/security-bonus-tool
D: feature/live-demo-ui
```

## Quy tắc phối hợp

- Không sửa cùng một file trên hai branch nếu chưa thống nhất.
- A đề xuất thay đổi schema trong issue của B.
- B đề xuất thay đổi prompt trong issue của A.
- E phối hợp với B về bonus tool schema, với C về eval và với D về UI trace.
- C chỉ ghi nhận metric từ run không có provider error và đo đủ toàn bộ cases.
- Người viết PR không tự review PR của mình.
- Nhóm trưởng giữ `main` luôn chạy được và chịu trách nhiệm merge.

Reviewer đề xuất:

| PR của | Reviewer |
|---|---|
| A | C và nhóm trưởng |
| B | C và E |
| C | A và nhóm trưởng |
| E | B và nhóm trưởng |
| Nhóm trưởng | A và C |

## Cập nhật hằng ngày

Mỗi người comment vào issue theo mẫu:

```text
Đã hoàn thành:
Đang làm:
Đang bị chặn bởi:
PR hoặc evidence:
Cần ai review:
```

## Điều kiện hoàn thành

- Acceptance criteria trong issue đã được đánh dấu đầy đủ.
- PR đã được review và merge.
- Test hoặc eval liên quan đã chạy thành công.
- Run và transcript có artifact version đúng.
- Không commit `.env`, API key, dữ liệu thật hoặc generated ticket.
- Mỗi thành viên có merged commit và self-reflection của chính mình.
