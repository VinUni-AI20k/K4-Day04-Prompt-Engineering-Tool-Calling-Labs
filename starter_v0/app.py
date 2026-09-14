"""Minimal Streamlit UI for the IT Helpdesk Agent (Role D — UI & Report Coordinator).

Reuses the same `run_model_tool_loop` used by chat.py and run_eval.py, so the
CLI, the eval evidence and this UI all execute the agent through one code
path — per LAB-GUIDE.md, section 9.

Run from the `starter_v0/` folder:

    streamlit run app.py

This file is a UI test surface only. It does not write artifacts/REPORT.md.

Only the controls actually required by README.md's UI row are exposed:
provider, a version label (for artifact_version + hashes), the chat itself
with per-round tool call/result detail, and the transcript path. Model
override and tool-round/history-window tuning are fixed constants below —
edit them directly in code if a run needs different values.
"""

from __future__ import annotations

import html
import json
from datetime import datetime
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini"]
TRANSCRIPTS_DIR = ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"

# Fixed run parameters (not exposed in the UI — edit here if needed).
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4

STATUS_LABELS = {
    "answered": "Đã trả lời",
    "waiting_for_user": "Đang chờ người dùng bổ sung",
    "max_tool_rounds": "Dừng do vượt số vòng gọi tool",
    "provider_error": "Lỗi provider",
}


def new_transcript_state(version: str, provider_name: str) -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    return {"id": transcript_id, "path": path, "created_at": now_iso()}


def esc(text: str) -> str:
    return html.escape(text).replace("\n", "<br>")


def parse_structured_reply(text: str) -> tuple[str, dict[str, Any] | None]:
    """system_prompt.md forces JSON output with a `reply` field. Show just
    that field in the chat bubble; keep the full object for the detail panel.
    Falls back to the raw text untouched if it isn't that JSON shape (e.g. a
    plain clarifying question)."""
    if not text:
        return "", None
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            data = json.loads(stripped)
        except (json.JSONDecodeError, TypeError):
            return text, None
        if isinstance(data, dict) and "reply" in data:
            return str(data.get("reply") or ""), data
    return text, None


st.set_page_config(page_title="IT Helpdesk Agent", layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .block-container {
        max-width: 760px;
        padding-top: 3rem;
        padding-bottom: 7rem;
    }
    section[data-testid="stSidebar"] {
        border-right: 1px solid #2A2A2A;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.75rem;
        max-width: none;
    }
    .brand {
        font-size: 1rem;
        font-weight: 600;
        color: #ECECEC;
        margin-bottom: 1.6rem;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: transparent;
        border: 1px solid #3A3A3A;
        color: #ECECEC;
        text-align: left;
        border-radius: 8px;
        margin-bottom: 1.6rem;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        border-color: #5B8DEF;
        color: #5B8DEF;
    }
    .sidebar-label {
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-size: 0.7rem;
        color: #8E8EA0;
        margin-top: 1.1rem;
        margin-bottom: 0.3rem;
    }
    .meta-block {
        margin-top: 2.2rem;
        padding-top: 1rem;
        border-top: 1px solid #2A2A2A;
    }
    .meta-line {
        font-size: 0.72rem;
        color: #8E8EA0;
        line-height: 1.5;
        word-break: break-all;
        margin-bottom: 0.75rem;
    }
    .empty-state {
        text-align: center;
        color: #8E8EA0;
        font-size: 1.05rem;
        margin-top: 22vh;
    }
    .msg {
        display: flex;
        margin: 0.9rem 0;
    }
    .msg-user {
        justify-content: flex-end;
    }
    .msg-user .bubble {
        background: #2F2F2F;
        color: #ECECEC;
        padding: 0.6rem 1rem;
        border-radius: 16px;
        max-width: 78%;
        line-height: 1.55;
    }
    .msg-assistant {
        color: #ECECEC;
        line-height: 1.65;
        width: 100%;
    }
    .status-line {
        font-size: 0.75rem;
        color: #8E8EA0;
        margin: 0.3rem 0 0.2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="brand">IT Helpdesk Agent</div>', unsafe_allow_html=True)

    if st.button("+  Cuộc trò chuyện mới", use_container_width=True):
        st.session_state["history"] = []
        st.session_state["turns"] = []
        st.session_state["transcript"] = new_transcript_state(
            st.session_state.get("version_label", "ui-test"),
            st.session_state.get("provider_name", "openrouter"),
        )
        st.rerun()

    st.markdown('<div class="sidebar-label">Provider</div>', unsafe_allow_html=True)
    provider_name = st.selectbox(
        "Provider",
        PROVIDERS,
        index=PROVIDERS.index(st.session_state.get("provider_name", "openrouter")),
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-label">Version label</div>', unsafe_allow_html=True)
    version_label = st.text_input(
        "Version label",
        value=st.session_state.get("version_label", "ui-test"),
        label_visibility="collapsed",
    )

    st.session_state["provider_name"] = provider_name
    st.session_state["version_label"] = version_label

    artifact_version = None
    try:
        artifact_version = build_artifact_version(
            version_label or "ui-test", SYSTEM_PROMPT_PATH, TOOLS_PATH
        )
    except FileNotFoundError as exc:
        st.error(f"Không đọc được artifact: {exc}")

    if "transcript" not in st.session_state:
        st.session_state["transcript"] = new_transcript_state(version_label or "ui-test", provider_name)

    meta_lines = []
    if artifact_version:
        meta_lines.append(
            f'<div class="meta-line">artifact_version<br>{artifact_version.artifact_version}</div>'
        )
    meta_lines.append(
        f'<div class="meta-line">transcript<br>{st.session_state["transcript"]["path"]}</div>'
    )
    st.markdown('<div class="meta-block">' + "".join(meta_lines) + "</div>", unsafe_allow_html=True)

st.session_state.setdefault("history", [])
st.session_state.setdefault("turns", [])

if not st.session_state["turns"]:
    st.markdown(
        '<div class="empty-state">Bạn cần hỗ trợ gì về IT?</div>',
        unsafe_allow_html=True,
    )

for turn in st.session_state["turns"]:
    st.markdown(
        f'<div class="msg msg-user"><div class="bubble">{esc(turn["user"])}</div></div>',
        unsafe_allow_html=True,
    )
    assistant_text = turn.get("assistant_text") or ""
    display_text, structured_reply = parse_structured_reply(assistant_text)
    st.markdown(
        f'<div class="msg msg-assistant">{esc(display_text)}</div>',
        unsafe_allow_html=True,
    )
    status_label = STATUS_LABELS.get(turn.get("status"), turn.get("status"))
    round_count = len(turn.get("rounds", []))
    st.markdown(
        f'<div class="status-line">{status_label} • {round_count} vòng gọi tool</div>',
        unsafe_allow_html=True,
    )
    if structured_reply or turn.get("rounds") or turn.get("artifact_version"):
        with st.expander("Chi tiết xử lý"):
            if turn.get("artifact_version"):
                st.caption(
                    f"artifact_version lúc trả lời: {turn['artifact_version']}"
                    f" • provider: {turn.get('provider')} • model: {turn.get('model')}"
                )
            if structured_reply:
                st.caption("Phản hồi có cấu trúc (JSON gốc từ model)")
                st.code(
                    json.dumps(structured_reply, ensure_ascii=False, indent=2),
                    language="json",
                )
            for round_record in turn["rounds"]:
                st.markdown(f"**Vòng {round_record['round']}**")
                if round_record.get("tool_calls"):
                    st.code(
                        json.dumps(round_record["tool_calls"], ensure_ascii=False, indent=2),
                        language="json",
                    )
                else:
                    st.caption("Không gọi tool nào ở vòng này.")
                for event in round_record.get("tool_results", []):
                    st.caption(f"Kết quả — {event.get('tool')}")
                    st.code(
                        json.dumps(event.get("result"), ensure_ascii=False, indent=2, default=str),
                        language="json",
                    )
    if turn.get("error"):
        st.error(turn["error"])

user_text = st.chat_input("Nhắn tin cho IT Helpdesk Agent...")

if user_text:
    if artifact_version is None:
        st.stop()

    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(TOOLS_PATH)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(provider_name)

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state["history"], HISTORY_WINDOW),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
        # Frozen at the moment this turn runs, so the transcript stays correct
        # evidence even if artifacts/provider change later in the same session.
        "artifact_version": artifact_version.artifact_version,
        "prompt_hash": artifact_version.prompt_hash,
        "tools_hash": artifact_version.tools_hash,
        "provider": provider_name,
        "model": getattr(provider, "default_model", None),
    }

    with st.spinner("Đang xử lý..."):
        try:
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=None,
                max_tool_rounds=MAX_TOOL_ROUNDS,
            )
            turn_record.update(result)
            assistant_text = result["assistant_text"]
            st.session_state["history"].append({"role": "user", "content": user_text})
            st.session_state["history"].append({"role": "assistant", "content": assistant_text})
        except Exception as exc:  # keep the UI alive; failures are evidence too
            turn_record.update(
                {
                    "status": "provider_error",
                    "assistant_text": "Đã xảy ra lỗi khi gọi model provider. Xem chi tiết bên dưới.",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    turn_record["ended_at"] = now_iso()
    st.session_state["turns"].append(turn_record)

    transcript_meta = st.session_state["transcript"]
    transcript = {
        "transcript_id": transcript_meta["id"],
        "version": version_label or "ui-test",
        "artifact_version": artifact_version.artifact_version,
        "prompt_hash": artifact_version.prompt_hash,
        "tools_hash": artifact_version.tools_hash,
        "provider": provider_name,
        "model": getattr(provider, "default_model", None),
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": HISTORY_WINDOW,
        "max_tool_rounds": MAX_TOOL_ROUNDS,
        "created_at": transcript_meta["created_at"],
        "turns": st.session_state["turns"],
    }
    write_transcript(transcript_meta["path"], transcript)

    st.rerun()
