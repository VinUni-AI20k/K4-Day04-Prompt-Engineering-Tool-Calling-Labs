from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ui import HelpdeskWebApp  # noqa: E402


SCENARIO = [
    "Kiểm tra trạng thái VPN production hiện tại.",
    "Kiểm tra kết nối VPN trên laptop của tôi.",
    "Mã máy là LT-318; hãy kiểm tra VPN trên máy này.",
    "Tạo ticket priority high cho LT-318, tóm tắt: VPN certificate sắp hết hạn.",
]


def main() -> None:
    app = HelpdeskWebApp(
        provider_name="openai",
        model=None,
        version="v3",
        system_prompt_path=ROOT / "artifacts" / "system_prompt.md",
        tools_path=ROOT / "artifacts" / "tools.yaml",
        max_tool_rounds=4,
        history_window=5,
    )
    for index, message in enumerate(SCENARIO, start=1):
        result = app.chat("rehearsal-v3", message)
        calls = [call for round_item in result["rounds"] for call in round_item["tool_calls"]]
        print(f"turn={index} status={result['status']} calls={calls}")
    print(f"transcript={ROOT / 'evidence' / 'transcripts' / 'rehearsal-v3.transcript.json'}")


if __name__ == "__main__":
    main()
