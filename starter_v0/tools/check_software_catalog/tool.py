from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err, fold_text, terms


CATALOG_FILE = ROOT / "helpdesk_data" / "software_catalog.json"
VALID_CATEGORIES = {"all", "communication", "developer_tools", "security", "utilities", "prohibited"}


def check_software_catalog(software_name: str = "", category: str = "all") -> dict[str, Any]:
    """Tra cứu trạng thái phê chuẩn phần mềm trong danh mục IT doanh nghiệp."""
    try:
        if not isinstance(software_name, str):
            return {"tool": "check_software_catalog", "error": "invalid_software_name_type"}
        if not isinstance(category, str):
            return {"tool": "check_software_catalog", "error": "invalid_category_type"}

        cleaned_name = (software_name or "").strip()
        cleaned_cat = (category or "all").strip().lower()

        if cleaned_cat not in VALID_CATEGORIES:
            return {
                "tool": "check_software_catalog",
                "error": "invalid_category",
                "supported_categories": sorted(VALID_CATEGORIES),
            }

        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        items = data["software_list"]

        if cleaned_cat != "all":
            items = [item for item in items if item["category"] == cleaned_cat]

        if not cleaned_name:
            # Liệt kê tất cả phần mềm theo category được chọn
            return {
                "tool": "check_software_catalog",
                "query": cleaned_name,
                "category": cleaned_cat,
                "total_found": len(items),
                "results": items,
            }

        search_terms = terms(cleaned_name)
        matched_items: list[dict[str, Any]] = []

        for item in items:
            item_name_folded = fold_text(item["name"])
            item_terms = terms(item["name"]) | terms(item["policy_notes"])

            # So khớp nếu tên chứa từ khóa hoặc có tập từ giao nhau
            if fold_text(cleaned_name) in item_name_folded or (search_terms and search_terms & item_terms):
                matched_items.append(item)

        if not matched_items:
            return {
                "tool": "check_software_catalog",
                "query": cleaned_name,
                "category": cleaned_cat,
                "error": "software_not_found",
                "message": f"Phần mềm '{cleaned_name}' chưa có trong danh mục. Yêu cầu tạo ticket để bộ phận IT đánh giá bảo mật.",
            }

        # Guardrail check: Nếu phần mềm bị cấm (prohibited), thêm cảnh báo an toàn rõ ràng
        has_prohibited = any(item["approval_status"] == "prohibited" for item in matched_items)

        return {
            "tool": "check_software_catalog",
            "query": cleaned_name,
            "category": cleaned_cat,
            "total_found": len(matched_items),
            "results": matched_items,
            "security_warning": "Phần mềm bị nghiêm cấm theo chính sách công ty!" if has_prohibited else None,
            "snapshot_at": data["snapshot_at"],
        }
    except Exception as exc:
        return err("check_software_catalog", exc)
