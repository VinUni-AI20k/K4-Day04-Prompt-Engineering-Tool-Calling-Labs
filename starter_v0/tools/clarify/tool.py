from __future__ import annotations
from typing import Any

def clarify(question: str = "", response_type: str = "text", options: list[str] | None = None) -> dict[str, Any]:
    return {
        "tool": "clarify",
        "question": question,
        "response_type": response_type,
        "options": options or [],
        "awaiting_user": True,
    }

SCHEMA = {
    "name": "clarify",
    "description": "Returns a question to the user and pauses until the next user turn. Use this to clarify information or confirm choices. 'response_type' can be free text, yes/no, or a choice from options.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Câu hỏi hoặc thông tin cần làm rõ gửi đến người dùng."
            },
            "response_type": {
                "type": "string",
                "description": "Loại phản hồi mong muốn từ người dùng (ví dụ: 'text', 'yes/no', 'choice'). Mặc định là 'text'."
            },
            "options": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Danh sách các tùy chọn. Chỉ bắt buộc sử dụng khi response_type là 'choice'."
            }
        },
        "required": ["question"]
    }
}