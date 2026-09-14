from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err, fold_text


ROOMS_FILE = ROOT / "helpdesk_data" / "meeting_rooms.json"
VALID_ASPECTS = {"all", "equipment", "av_status", "network", "issues"}


def inspect_meeting_room(room_id: str = "", aspect: str = "all") -> dict[str, Any]:
    """Kiểm tra trang thiết bị nghe nhìn và trạng thái kỹ thuật của phòng họp."""
    try:
        if not isinstance(room_id, str):
            return {"tool": "inspect_meeting_room", "error": "invalid_room_id_type"}
        if not isinstance(aspect, str):
            return {"tool": "inspect_meeting_room", "error": "invalid_aspect_type"}

        cleaned_id = (room_id or "").strip().upper()
        cleaned_aspect = (aspect or "all").strip().lower()

        if cleaned_aspect not in VALID_ASPECTS:
            return {
                "tool": "inspect_meeting_room",
                "error": "invalid_aspect",
                "supported_aspects": sorted(VALID_ASPECTS),
            }

        data = json.loads(ROOMS_FILE.read_text(encoding="utf-8"))
        rooms = data["rooms"]

        # Tìm theo mã phòng (MR-xxx) hoặc tìm theo tên phòng (không dấu)
        matched_room = None
        for room in rooms:
            if room["room_id"] == cleaned_id or fold_text(cleaned_id) in fold_text(room["name"]):
                matched_room = room
                break

        if matched_room is None:
            return {
                "tool": "inspect_meeting_room",
                "room_id": cleaned_id,
                "error": "room_not_found",
                "available_rooms": [f"{r['room_id']}: {r['name']}" for r in rooms],
            }

        # Lọc thông tin theo aspect được yêu cầu
        details: dict[str, Any] = {
            "room_id": matched_room["room_id"],
            "name": matched_room["name"],
            "location": matched_room["location"],
            "capacity": matched_room["capacity"],
        }

        if cleaned_aspect in {"all", "equipment"}:
            details["equipment"] = matched_room["equipment"]
            details["display_input"] = matched_room.get("display_input")

        if cleaned_aspect in {"all", "av_status"}:
            details["av_status"] = matched_room["av_status"]

        if cleaned_aspect in {"all", "network"}:
            details["network_status"] = matched_room["network_status"]

        if cleaned_aspect in {"all", "issues"}:
            details["known_issues"] = matched_room["known_issues"]

        return {
            "tool": "inspect_meeting_room",
            "aspect": cleaned_aspect,
            **details,
            "snapshot_at": data["snapshot_at"],
        }
    except Exception as exc:
        return err("inspect_meeting_room", exc)
