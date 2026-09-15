"""Streamlit chat UI for the IT Helpdesk Agent.

Reuses `run_model_tool_loop` from chat.py so the UI, the CLI chat and the eval
runner share exactly one agent loop. Every turn is appended to a transcript JSON
under transcripts/ using the same schema as chat.py.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
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


PROVIDERS = ["gemini", "openrouter", "openai", "anthropic"]
DEFAULT_MODELS = {"gemini": "gemini-3.5-flash-lite", "openrouter": "", "openai": "", "anthropic": ""}
TRANSCRIPTS_DIR = ROOT / "transcripts"


# ---------------------------------------------------------------- helpers

def parse_agent_json(text: str) -> dict[str, Any] | None:
    """The system prompt asks for a JSON answer; it may arrive inside a ```json fence."""
    if not text:
        return None
    candidate = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", candidate, re.DOTALL)
    if fence:
        candidate = fence.group(1)
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def new_transcript(cfg: dict[str, Any]) -> tuple[dict[str, Any], Path]:
    artifact = build_artifact_version(cfg["version"], cfg["system_prompt_path"], cfg["tools_path"])
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(cfg["version"]), safe_slug(cfg["provider"]), "ui", timestamp])
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": cfg["provider"],
        "model": cfg["model"],
        "system_prompt": str(cfg["system_prompt_path"]),
        "tools": str(cfg["tools_path"]),
        "history_window": cfg["history_window"],
        "max_tool_rounds": cfg["max_tool_rounds"],
        "interface": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"


def reset_conversation(cfg: dict[str, Any]) -> None:
    st.session_state.history = []          # user/assistant pairs fed back to the model
    st.session_state.turn_records = []     # full per-turn records for rendering
    st.session_state.transcript, st.session_state.transcript_path = new_transcript(cfg)
    st.session_state.turn_index = 0


def render_tool_event(event: dict[str, Any]) -> None:
    result = event.get("result", {})
    is_error = isinstance(result, dict) and result.get("error")
    icon = "❌" if is_error else "✅"
    st.markdown(f"{icon} **`{event['tool']}`**")
    st.caption("args")
    st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
    st.caption("result" + (f" — error: `{result.get('error')}`" if is_error else ""))
    st.code(json.dumps(result, ensure_ascii=False, indent=2, default=str)[:6000], language="json")


def render_turn(record: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(record["user"])
    with st.chat_message("assistant"):
        status = record.get("status")
        if status == "provider_error":
            st.error(record.get("error", "provider error"))
            return

        text = record.get("assistant_text") or ""
        parsed = parse_agent_json(text)
        if parsed and "reply" in parsed:
            st.markdown(str(parsed["reply"]))
            meta = " · ".join(
                f"**{key}:** `{parsed.get(key)}`" for key in ("intent", "action") if parsed.get(key) is not None
            )
            evidence = parsed.get("evidence_ids") or []
            if evidence:
                meta += " · **evidence:** " + ", ".join(f"`{item}`" for item in evidence)
            if meta:
                st.caption(meta)
        else:
            st.markdown(text or "_(no text)_")

        badge = {"answered": "🟢", "waiting_for_user": "🟡", "max_tool_rounds": "🔴"}.get(status, "⚪")
        events = record.get("tool_events", [])
        rounds = record.get("rounds", [])
        label = f"{badge} status: {status} · rounds: {len(rounds)} · tool calls: {len(events)}"
        with st.expander(label, expanded=bool(events)):
            if not events:
                st.caption("No tool was called for this turn.")
            for round_record in rounds:
                st.markdown(f"**Round {round_record['round']}**")
                if round_record.get("assistant_text") and not round_record.get("tool_calls"):
                    st.caption("final answer produced in this round")
                for event in round_record.get("tool_results", []):
                    render_tool_event(event)
            if parsed is None and text:
                st.caption("raw assistant text")
                st.code(text)
            elif parsed is not None:
                st.caption("raw JSON answer")
                st.code(json.dumps(parsed, ensure_ascii=False, indent=2), language="json")


# ---------------------------------------------------------------- sidebar

st.set_page_config(page_title="IT Helpdesk Agent", page_icon="🛠️", layout="wide")

with st.sidebar:
    st.title("🛠️ IT Helpdesk Agent")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model_name = st.text_input("Model (blank = provider default)", value=DEFAULT_MODELS.get(provider_name, ""))
    version_label = st.text_input("Artifact version label", value="v5")
    system_prompt_path = Path(st.text_input("System prompt", value=str(ARTIFACTS_DIR / "system_prompt.md")))
    tools_path = Path(st.text_input("Tool declarations", value=str(ARTIFACTS_DIR / "tools.yaml")))
    history_window = st.slider("History window (user/assistant pairs)", 0, 10, 5)
    max_tool_rounds = st.slider("Max tool rounds per turn", 1, 8, 4)

    cfg = {
        "provider": provider_name,
        "model": model_name.strip() or None,
        "version": version_label.strip() or "v0",
        "system_prompt_path": system_prompt_path,
        "tools_path": tools_path,
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
    }

    if "transcript" not in st.session_state:
        reset_conversation(cfg)
    if st.button("🔄 New conversation", use_container_width=True):
        reset_conversation(cfg)
        st.rerun()

    st.divider()
    st.subheader("Artifact version")
    try:
        artifact = build_artifact_version(cfg["version"], system_prompt_path, tools_path)
        st.code(artifact.artifact_version)
        st.caption(f"prompt sha256: `{artifact.prompt_hash[:16]}…`")
        st.caption(f"tools sha256: `{artifact.tools_hash[:16]}…`")
    except FileNotFoundError as exc:
        st.error(f"Artifact not found: {exc}")

    st.subheader("Transcript")
    st.code(str(st.session_state.transcript_path.relative_to(ROOT)))
    st.caption(f"turns saved: {len(st.session_state.transcript['turns'])}")


# ---------------------------------------------------------------- main

st.caption(
    "Same agent loop as `chat.py` / `run_eval.py`. Each turn shows tool calls, arguments, results and the "
    "artifact version so behaviour can be audited."
)

for record in st.session_state.turn_records:
    render_turn(record)

user_text = st.chat_input("Ask the IT service desk… (e.g. 'VPN production có đang lỗi không?')")
if user_text:
    try:
        system_prompt = system_prompt_path.read_text(encoding="utf-8")
        openai_tools = to_openai_tools(load_tool_declarations(tools_path))
        provider = make_provider(provider_name)
    except Exception as exc:
        st.error(f"Setup error: {type(exc).__name__}: {exc}")
        st.stop()

    st.session_state.turn_index += 1
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]
    record: dict[str, Any] = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("user"):
        st.markdown(user_text)
    with st.chat_message("assistant"):
        with st.spinner("Running agent loop…"):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=cfg["model"],
                    max_tool_rounds=max_tool_rounds,
                )
                record.update(result)
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
            except Exception as exc:
                record.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})

    record["ended_at"] = now_iso()
    st.session_state.turn_records.append(record)
    st.session_state.transcript["turns"].append(record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
    st.rerun()
