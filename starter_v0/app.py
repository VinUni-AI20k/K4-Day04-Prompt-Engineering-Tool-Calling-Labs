"""IT Helpdesk Agent — Streamlit UI (v2, bản updated).

Bản đầy đủ tính năng: cấu hình history window / max tool rounds, nhãn trạng thái
tool (error / needs_confirmation / awaiting_user) nổi bật, tóm tắt metrics mỗi
turn, reset hội thoại, và tải transcript về làm evidence.

Tái sử dụng cùng `run_model_tool_loop` với CLI/eval để UI không lệch hành vi
(xem TOOL-SETUP.md §10). Không dùng `use_container_width` (đã deprecated) — dùng
`width="stretch"`.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
PROVIDERS = ["openrouter", "openai", "anthropic", "gemini"]

load_lab_env(ROOT)

st.set_page_config(
    page_title="IT Helpdesk Agent",
    page_icon=":material/support_agent:",
    layout="wide",
)


# --------------------------------------------------------------------------- #
# Rendering helpers
# --------------------------------------------------------------------------- #
def result_label(tool: str, result: Any) -> str:
    """Label a tool event so errors / action boundaries stand out at a glance."""
    if isinstance(result, dict):
        if result.get("error"):
            return f":material/error: {tool} — error: {result.get('error')}"
        status = result.get("status")
        if status == "needs_confirmation":
            return f":material/hourglass_top: {tool} — needs_confirmation"
        if status == "created":
            return f":material/check_circle: {tool} — created"
        if result.get("awaiting_user"):
            return f":material/pause_circle: {tool} — awaiting_user"
    return f":material/build: {tool}"


def render_tool_event(event: dict[str, Any]) -> None:
    result = event.get("result", {})
    is_error = isinstance(result, dict) and bool(result.get("error"))
    with st.expander(result_label(event.get("tool", "?"), result), expanded=is_error):
        st.caption("Arguments")
        st.json(event.get("args", {}))
        st.caption("Result" if not is_error else "Error")
        st.json(result)


def turn_metrics(turn: dict[str, Any]) -> tuple[int, int]:
    """Đếm số tool call và số error trong một turn để hiển thị metrics."""
    calls = errors = 0
    for rnd in turn.get("rounds", []):
        for event in rnd.get("tool_results", []):
            calls += 1
            result = event.get("result", {})
            if isinstance(result, dict) and result.get("error"):
                errors += 1
    return calls, errors


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])

    with st.chat_message("assistant"):
        status = turn.get("status")
        if status == "waiting_for_user":
            st.info(":material/pause_circle: Đang chờ người dùng bổ sung thông tin (clarify).")
        elif status == "max_tool_rounds":
            st.warning(":material/warning: Dừng sau khi đạt max tool rounds.")
        elif status == "provider_error":
            st.error(turn.get("error") or "Provider error")

        if turn.get("assistant_text"):
            st.markdown(turn["assistant_text"])

        calls, errors = turn_metrics(turn)
        if calls:
            cols = st.columns(3)
            cols[0].metric("Tool calls", calls)
            cols[1].metric("Errors", errors)
            cols[2].metric("Rounds", len(turn.get("rounds", [])))

        for rnd in turn.get("rounds", []):
            events = rnd.get("tool_results", [])
            if not events:
                continue
            st.caption(f"Round {rnd.get('round')} — {len(events)} tool call(s)")
            for event in events:
                render_tool_event(event)


# --------------------------------------------------------------------------- #
# Session bootstrap
# --------------------------------------------------------------------------- #
def new_transcript(version: str, provider: str, model: str | None, artifact_version) -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider), timestamp])
    return {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider,
        "model": model,
        "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
        "tools": str(ARTIFACTS_DIR / "tools.yaml"),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def reset_conversation() -> None:
    for key in ("history", "display_turns", "transcript", "turn_index", "transcript_path"):
        st.session_state.pop(key, None)


# --------------------------------------------------------------------------- #
# Sidebar — configuration & artifact version
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("Cấu hình run")
    version = st.text_input("Artifact version", value="v0", help="Nhãn version của nhóm, vd v0/v1/v2/v3.")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model_input = st.text_input("Model (trống = default)", value="")
    model = model_input.strip() or None
    history_window = st.number_input("History window (số cặp)", min_value=0, max_value=20, value=5)
    max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=10, value=4)

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)

    st.divider()
    st.caption("Artifact version (prompt+tools hash)")
    st.code(artifact_version.artifact_version, language="text")

    st.button(
        "Reset conversation",
        icon=":material/refresh:",
        on_click=reset_conversation,
        width="stretch",
    )

# Load declarations fresh each run so prompt/tools edits are reflected live.
system_prompt = system_prompt_path.read_text(encoding="utf-8")
openai_tools = to_openai_tools(load_tool_declarations(tools_path))

# Initialize session state (also re-inits after a reset).
if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.display_turns = []
    st.session_state.turn_index = 0
    st.session_state.transcript = new_transcript(version, provider_name, model, artifact_version)


# --------------------------------------------------------------------------- #
# Main pane
# --------------------------------------------------------------------------- #
st.title("IT Helpdesk Agent")
st.caption(
    f"provider=`{provider_name}` · model=`{model or 'default'}` · "
    f"artifact=`{artifact_version.artifact_version}`"
)

for turn in st.session_state.display_turns:
    render_turn(turn)

user_text = st.chat_input("Nhập yêu cầu helpdesk…")
if user_text:
    st.session_state.turn_index += 1
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, int(history_window)),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    provider = make_provider(provider_name)
    try:
        with st.spinner("Agent đang xử lý…"):
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=model,
                max_tool_rounds=int(max_tool_rounds),
            )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": assistant_text})
    except Exception as exc:  # provider error is evidence, not a crash
        turn_record.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})

    turn_record["ended_at"] = now_iso()
    st.session_state.display_turns.append(turn_record)
    st.session_state.transcript["turns"].append(turn_record)

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    transcript_path = TRANSCRIPTS_DIR / f"{st.session_state.transcript['transcript_id']}.transcript.json"
    write_transcript(transcript_path, st.session_state.transcript)
    st.session_state.transcript_path = str(transcript_path)

    st.rerun()

# Transcript download / path (evidence for submission).
if st.session_state.get("transcript_path"):
    path = Path(st.session_state.transcript_path)
    with st.sidebar:
        st.divider()
        st.caption("Transcript")
        st.code(str(path), language="text")
        if path.exists():
            st.download_button(
                "Download transcript",
                icon=":material/download:",
                data=path.read_text(encoding="utf-8"),
                file_name=path.name,
                mime="application/json",
                width="stretch",
            )
