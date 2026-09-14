"""Streamlit UI for the IT Helpdesk Agent.

Run from ``starter_v0`` with ``streamlit run ui.py``.  The UI intentionally
uses the same ``run_model_tool_loop`` as the CLI so its transcripts show the
same tool behaviour as a live chat session.
"""

from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
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
from versioning import artifact_version_dict, build_artifact_version


TRANSCRIPTS_DIR = ROOT / "transcripts"
DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "openrouter": "openai/gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "gemini": "gemini-2.0-flash",
}


def configured_provider_default() -> str:
    """Prefer a provider for which this session actually has a configured key."""
    key_by_provider = {
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }
    for provider_name, env_name in key_by_provider.items():
        if os.getenv(env_name):
            return provider_name
    return "openai"


def make_transcript(
    *,
    version: str,
    provider_name: str,
    model: str,
    history_window: int,
    max_tool_rounds: int,
) -> tuple[dict[str, Any], Path]:
    """Create one transcript document for a UI chat session."""
    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact = build_artifact_version(version, prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        "ui",
        safe_slug(version),
        safe_slug(provider_name),
        timestamp,
    ])
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"


def reset_session(
    *,
    version: str,
    provider_name: str,
    model: str,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    transcript, transcript_path = make_transcript(
        version=version,
        provider_name=provider_name,
        model=model,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )
    st.session_state.transcript = transcript
    st.session_state.transcript_path = transcript_path
    st.session_state.history = []


def ensure_session(
    *,
    version: str,
    provider_name: str,
    model: str,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    if "transcript" not in st.session_state:
        reset_session(
            version=version,
            provider_name=provider_name,
            model=model,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
        )


def render_trace(turn: dict[str, Any]) -> None:
    """Render every model round and every executed tool event for auditing."""
    status = turn.get("status", "unknown")
    with st.expander(f"Trace — turn {turn.get('turn_index')} · {status}"):
        st.caption(f"Started: {turn.get('started_at', '—')} · Ended: {turn.get('ended_at', '—')}")
        if turn.get("error"):
            st.error(turn["error"])
        for round_record in turn.get("rounds", []):
            st.markdown(f"**Round {round_record['round']}**")
            if round_record.get("assistant_text"):
                st.write(round_record["assistant_text"])
            calls = round_record.get("tool_calls", [])
            if calls:
                st.markdown("Tool calls")
                st.json(calls, expanded=False)
            for event in round_record.get("tool_results", []):
                label = event.get("tool", "unknown_tool")
                with st.container(border=True):
                    st.markdown(f"`{label}`")
                    st.caption("Arguments")
                    st.json(event.get("args", {}), expanded=False)
                    result = event.get("result", {})
                    if isinstance(result, dict) and result.get("error"):
                        st.error(f"Tool error: {result['error']}")
                    st.caption("Result")
                    st.json(result, expanded=False)


def render_conversation() -> None:
    for turn in st.session_state.transcript["turns"]:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            st.write(turn.get("assistant_text") or "No response was returned.")
        render_trace(turn)


def run_turn(
    user_text: str,
    *,
    provider_name: str,
    model: str,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    """Run and persist exactly one user turn using the shared agent loop."""
    transcript = st.session_state.transcript
    turn_record: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
        declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
        provider = make_provider(provider_name)
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, history_window),
            {"role": "user", "content": user_text},
        ]
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=to_openai_tools(declarations),
            model=model,
            max_tool_rounds=max_tool_rounds,
        )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
        st.session_state.history.extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_text},
        ])
    except Exception as exc:
        turn_record.update({
            "status": "provider_error",
            "error": f"{type(exc).__name__}: {exc}",
            "assistant_text": "Provider error. Inspect the trace, then check the selected API key and model.",
        })

    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, transcript)


def main() -> None:
    st.set_page_config(page_title="Northstar IT Helpdesk", page_icon="🛠️", layout="wide")
    st.title("🛠️ Northstar IT Helpdesk Agent")
    st.caption("Live chat with auditable tool calls. Never enter secrets, passwords, or real customer data.")

    with st.sidebar:
        st.header("Session settings")
        provider_options = list(DEFAULT_MODELS)
        provider_name = st.selectbox(
            "Provider",
            provider_options,
            index=provider_options.index(configured_provider_default()),
        )
        model = st.text_input("Model", value=DEFAULT_MODELS[provider_name]).strip()
        version = st.text_input("Artifact version", value="v3").strip() or "v3"
        history_window = st.slider("History window (pairs)", min_value=1, max_value=10, value=5)
        max_tool_rounds = st.slider("Maximum tool rounds", min_value=1, max_value=8, value=4)
        if st.button("Start new conversation", use_container_width=True):
            reset_session(
                version=version,
                provider_name=provider_name,
                model=model,
                history_window=history_window,
                max_tool_rounds=max_tool_rounds,
            )
            st.rerun()

    ensure_session(
        version=version,
        provider_name=provider_name,
        model=model,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )
    transcript = st.session_state.transcript

    with st.sidebar:
        st.header("Artifact evidence")
        st.caption(f"Version: `{transcript['artifact_version']}`")
        st.caption(f"Prompt SHA-256: `{transcript['prompt_hash']}`")
        st.caption(f"Tools SHA-256: `{transcript['tools_hash']}`")
        st.caption(f"Transcript: `{st.session_state.transcript_path}`")
        if st.button("Save transcript now", use_container_width=True):
            write_transcript(st.session_state.transcript_path, transcript)
            st.success("Transcript saved.")

    render_conversation()
    user_text = st.chat_input("Describe an IT issue or ask an IT policy question…")
    if user_text:
        with st.spinner("Running the shared tool loop…"):
            run_turn(
                user_text.strip(),
                provider_name=provider_name,
                model=model,
                history_window=history_window,
                max_tool_rounds=max_tool_rounds,
            )
        st.rerun()


if __name__ == "__main__":
    main()
