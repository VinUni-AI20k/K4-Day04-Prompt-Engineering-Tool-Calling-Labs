from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.search_device_info.tool import search_device_info  # noqa: E402


def assert_error(result: dict, expected: str) -> None:
    actual = result.get("error")
    if actual != expected:
        raise AssertionError(f"expected error={expected!r}, got {actual!r}: {result}")


def main() -> None:
    original_key = os.environ.pop("TAVILY_API_KEY", None)
    try:
        blocked = search_device_info("Lenovo", "LT-240 ThinkPad T14", "support")
        assert_error(blocked, "restricted_internal_identifier")

        missing_key = search_device_info("Lenovo", "ThinkPad T14 Gen 4", "drivers")
        assert_error(missing_key, "missing_api_key")

        invalid_type = search_device_info("Lenovo", "ThinkPad T14 Gen 4", "firmware")
        assert_error(invalid_type, "invalid_query_type")
    finally:
        if original_key is not None:
            os.environ["TAVILY_API_KEY"] = original_key

    print("bonus smoke test passed: privacy guardrail, missing-key path, enum validation")


if __name__ == "__main__":
    main()
