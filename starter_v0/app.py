from __future__ import annotations

import json
from html import escape
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

CONFIG = {
    "version": "v3",
    "provider": "openai",
    "history_window": 5,
    "max_tool_rounds": 4,
}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def reply_only(text: str | None) -> str:
    candidate = (text or "").strip()
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return candidate
    return parsed.get("reply", candidate) if isinstance(parsed, dict) else candidate


def create_transcript() -> tuple[dict[str, Any], Path]:
    artifact = build_artifact_version(CONFIG["version"], SYSTEM_PROMPT_PATH, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    path = TRANSCRIPTS_DIR / f"v3_openai_{timestamp}.transcript.json"
    transcript = {
        "transcript_id": path.stem,
        **artifact_version_dict(artifact),
        "provider": CONFIG["provider"],
        "model": None,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": CONFIG["history_window"],
        "max_tool_rounds": CONFIG["max_tool_rounds"],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
        "source": "streamlit_ui",
    }
    return transcript, path


def initialize_chat() -> None:
    if "turns" in st.session_state:
        return
    transcript, path = create_transcript()
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.transcript = transcript
    st.session_state.transcript_path = path


def write_transcript() -> None:
    transcript = st.session_state.transcript
    transcript["updated_at"] = now_iso()
    path = st.session_state.transcript_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")


def submit_request(user_text: str) -> None:
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    declarations = load_tool_declarations(TOOLS_PATH)
    provider = make_provider(CONFIG["provider"])
    selected_model = getattr(provider, "default_model", None)
    messages = [
        {"role": "system", "content": system_prompt},
        *st.session_state.history[-CONFIG["history_window"] * 2 :],
        {"role": "user", "content": user_text},
    ]
    turn: dict[str, Any] = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": "",
        "rounds": [],
        "tool_events": [],
    }
    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=to_openai_tools(declarations),
            model=selected_model,
            max_tool_rounds=CONFIG["max_tool_rounds"],
        )
        turn.update(result)
        st.session_state.history.extend(
            [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": result["assistant_text"]},
            ]
        )
        st.session_state.transcript["model"] = selected_model
    except Exception as exc:
        turn.update(
            {
                "status": "provider_error",
                "assistant_text": "",
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
    turn["ended_at"] = now_iso()
    st.session_state.turns.append(turn)
    st.session_state.transcript["turns"].append(turn)
    write_transcript()


def render_trace(turns: list[dict[str, Any]]) -> None:
    if not any(turn.get("tool_events") for turn in turns):
        st.caption("Chưa có tool call trong cuộc hội thoại.")
        return
    for turn in turns:
        for index, event in enumerate(turn.get("tool_events", []), start=1):
            tool = event.get("tool", "unknown_tool")
            with st.expander(f"Lượt {turn['turn_index']} · {index} · {tool}", expanded=True):
                st.caption("Tool call")
                st.json({"name": tool, "args": event.get("args", {})})
                st.caption("Tool result")
                result = event.get("result", {})
                if isinstance(result, dict) and result.get("error"):
                    st.error(result.get("message") or result["error"])
                st.json(result)


def main() -> None:
    st.set_page_config(page_title="Northstar Labs Helpdesk Agent", page_icon="NL", layout="wide")
    initialize_chat()
    artifact = build_artifact_version(CONFIG["version"], SYSTEM_PROMPT_PATH, TOOLS_PATH)

    st.markdown(
        """
        <style>
        .block-container { max-width: 1500px; padding-top: 1.5rem; }
        [data-testid="stChatMessage"] { border: 1px solid #d9e2ef; border-radius: 8px; padding: 0.4rem 0.75rem; }
        .transcript-path { font-family: monospace; font-size: 0.78rem; overflow-wrap: anywhere; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    header, clear = st.columns([6, 1])
    with header:
        st.title("Northstar Labs Helpdesk Agent")
        st.caption(f"Artifact {artifact.artifact_version}")
    with clear:
        st.write("")
        st.write("")
        if st.button("Xóa chat", use_container_width=True):
            for key in ("turns", "history", "transcript", "transcript_path"):
                st.session_state.pop(key, None)
            st.rerun()

    conversation, trace = st.columns([2, 1], gap="large")
    with conversation:
        st.subheader("Hội thoại")
        for turn in st.session_state.turns:
            with st.chat_message("user"):
                st.write(turn["user"])
            with st.chat_message("assistant"):
                if turn.get("status") == "provider_error":
                    st.error(turn.get("error", "Provider error"))
                else:
                    st.write(reply_only(turn.get("assistant_text")))
        with st.form("request_form", clear_on_submit=True):
            request = st.text_area("Yêu cầu helpdesk", placeholder="Nhập yêu cầu helpdesk...", label_visibility="collapsed")
            submitted = st.form_submit_button("Gửi", use_container_width=True)
        if submitted and request.strip():
            with st.spinner("Agent đang xử lý..."):
                submit_request(request.strip())
            st.rerun()

    with trace:
        st.subheader("Trace log")
        render_trace(st.session_state.turns)
        st.caption("Transcript path")
        st.markdown(
            f'<div class="transcript-path">{escape(str(st.session_state.transcript_path))}</div>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
