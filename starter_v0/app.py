"""IT Helpdesk Agent — Streamlit UI (v1, bản cơ bản).

Bản tối giản: chat multi-turn, cấu hình gọn trong sidebar, hiển thị tool call
dưới dạng expander đơn giản. Tái sử dụng cùng `run_model_tool_loop` với CLI/eval
để UI không lệch hành vi (xem TOOL-SETUP.md §10).
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

st.set_page_config(page_title="IT Helpdesk Agent (v1)", page_icon=":material/support_agent:")


# --------------------------------------------------------------------------- #
# Rendering helpers
# --------------------------------------------------------------------------- #
def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])

    with st.chat_message("assistant"):
        status = turn.get("status")
        if status == "waiting_for_user":
            st.info("Đang chờ người dùng bổ sung thông tin (clarify).")
        elif status == "max_tool_rounds":
            st.warning("Dừng sau khi đạt max tool rounds.")
        elif status == "provider_error":
            st.error(turn.get("error") or "Provider error")

        if turn.get("assistant_text"):
            st.markdown(turn["assistant_text"])

        for rnd in turn.get("rounds", []):
            for event in rnd.get("tool_results", []):
                tool = event.get("tool", "?")
                result = event.get("result", {})
                is_error = isinstance(result, dict) and bool(result.get("error"))
                label = f"{tool} — error" if is_error else tool
                with st.expander(label, expanded=is_error):
                    st.caption("Arguments")
                    st.json(event.get("args", {}))
                    st.caption("Result")
                    st.json(result)


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


# --------------------------------------------------------------------------- #
# Sidebar — configuration
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("Cấu hình run")
    version = st.text_input("Artifact version", value="v0", help="Nhãn version của nhóm, vd v0/v1/v2/v3.")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model_input = st.text_input("Model (trống = default)", value="")
    model = model_input.strip() or None

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)

    st.divider()
    st.caption("Artifact version (prompt+tools hash)")
    st.code(artifact_version.artifact_version, language="text")

# Load declarations fresh each run so prompt/tools edits are reflected live.
system_prompt = system_prompt_path.read_text(encoding="utf-8")
openai_tools = to_openai_tools(load_tool_declarations(tools_path))

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.display_turns = []
    st.session_state.turn_index = 0
    st.session_state.transcript = new_transcript(version, provider_name, model, artifact_version)


# --------------------------------------------------------------------------- #
# Main pane
# --------------------------------------------------------------------------- #
st.title("IT Helpdesk Agent")
st.caption(f"provider=`{provider_name}` · model=`{model or 'default'}`")

for turn in st.session_state.display_turns:
    render_turn(turn)

user_text = st.chat_input("Nhập yêu cầu helpdesk…")
if user_text:
    st.session_state.turn_index += 1
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, 5),
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
                max_tool_rounds=4,
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

    st.rerun()
