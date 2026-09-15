from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 30
INTERNAL_IDENTIFIER = re.compile(r"\b(?:LT|DT|MB|PR|RM|EMP)-\d+\b", re.IGNORECASE)
SENSITIVE_VALUE = re.compile(r"\b(?:password|passwd|token|api[ _-]?key|mfa|otp|recovery[ _-]?code)\s*[:=]", re.IGNORECASE)


def err(tool: str, exc: Exception) -> dict[str, Any]:
    return {"tool": tool, "error": type(exc).__name__, "message": str(exc)}


def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def fold_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def terms(text: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to",
        "ban", "bao", "can", "cho", "co", "cua", "duoc", "gi", "giup", "la", "lam", "minh", "mot", "nay",
        "nen", "the", "thi", "trong", "va", "ve", "voi",
    }
    folded = fold_text(text)
    return {term for term in re.findall(r"[a-z0-9]+", folded) if len(term) > 1 and term not in stopwords}


def latest_user_text(messages: list[dict[str, str]]) -> str:
    """Return only the current user request, excluding stale conversation context."""
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        content = message.get("content", "")
        marker = "Latest user turn to answer now:"
        if marker in content:
            return content.rsplit(marker, 1)[1].strip()
        return content
    return ""


def has_explicit_confirmation(text: str) -> bool:
    folded = fold_text(text)
    if "tool_results_json" in folded or "confirmed=true" in folded or "confirmed: true" in folded:
        return False
    return bool(re.search(r"\b(?:toi|minh)\s+(?:xac nhan|dong y|cho phep)\b", folded))


def external_identifier_smuggling(text: str) -> bool:
    folded = fold_text(text)
    return bool(INTERNAL_IDENTIFIER.search(text)) and any(
        marker in folded
        for marker in ("giu nguyen", "them ma", "gui asset", "send asset", "query web", "truyen ra web")
    )
