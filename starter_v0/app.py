from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

PROVIDER_ENV_VARS = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


def initialize_state() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("turns", [])
    st.session_state.setdefault("transcript_path", None)


def new_transcript(version: str, provider: str, model: str | None, artifact: Any) -> dict[str, Any]:
    return {
        "transcript_id": f"ui_{datetime.now().strftime('%Y%m%dT%H%M%S%f')}",
        **artifact_version_dict(artifact),
        "provider": provider,
        "model": model,
        "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
        "tools": str(ARTIFACTS_DIR / "tools.yaml"),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "turns": [],
    }


def render_event(event: dict[str, Any]) -> None:
    tool_name = event.get("tool", "unknown_tool")
    args = event.get("args", {})
    result = event.get("result", {})
    with st.expander(f"{tool_name}  {json.dumps(args, ensure_ascii=False)}", expanded=False):
        st.write("Arguments")
        st.json(args)
        if isinstance(result, dict) and result.get("error"):
            st.error(f"{result.get('error')}: {result.get('message', '')}")
        else:
            st.write("Tool result")
            st.json(result)


def main() -> None:
    st.set_page_config(page_title="Northstar Helpdesk Agent", page_icon="IT", layout="wide")
    initialize_state()

    st.title("Northstar IT Helpdesk Agent")
    st.caption("Live trace UI for prompt, tool-calling, multi-turn and safety evidence")

    with st.sidebar:
        st.header("Run configuration")
        provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
        provider_env = PROVIDER_ENV_VARS[provider_name]
        if os.getenv(provider_env):
            st.success(f"{provider_env} is configured")
        else:
            st.warning(f"Missing {provider_env}")
            st.caption("Create starter_v0/.env, add the provider key, then restart Streamlit. Never commit .env.")
        model = st.text_input("Model override", value="", help="Leave empty to use the provider default.")
        version = st.text_input("Artifact version label", value="v3")
        max_rounds = st.number_input("Max tool rounds", min_value=1, max_value=8, value=4)
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.history = []
            st.session_state.turns = []
            st.session_state.transcript_path = None
            st.rerun()

    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = prompt_path.read_text(encoding="utf-8")
    artifact = build_artifact_version(version, prompt_path, tools_path)
    st.info(f"Artifact: `{artifact.artifact_version}`  |  prompt `{artifact.prompt_hash[:12]}`  |  tools `{artifact.tools_hash[:12]}`")

    for turn in st.session_state.turns:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            st.write(turn.get("assistant_text") or "")
            st.caption(f"status={turn.get('status', 'unknown')}")
            for event in turn.get("tool_events", []):
                render_event(event)

    user_text = st.chat_input("Describe the IT helpdesk request")
    if not user_text:
        return

    with st.chat_message("user"):
        st.write(user_text)

    try:
        required_env = PROVIDER_ENV_VARS[provider_name]
        if not os.getenv(required_env):
            raise RuntimeError(
                f"Missing {required_env}. Copy .env.example to .env, fill the selected provider key, and restart Streamlit."
            )
        provider = make_provider(provider_name)
        selected_model = model.strip() or getattr(provider, "default_model", None)
        declarations = load_tool_declarations(tools_path)
        openai_tools = to_openai_tools(declarations)
        messages = [
            {"role": "system", "content": system_prompt},
            *st.session_state.history[-10:],
            {"role": "user", "content": user_text},
        ]
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model.strip() or None,
            max_tool_rounds=int(max_rounds),
        )
    except Exception as exc:
        result = {
            "status": "provider_error",
            "assistant_text": f"Provider error: {type(exc).__name__}: {exc}",
            "rounds": [],
            "tool_events": [],
        }

    turn = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "user": user_text,
        **result,
        "ended_at": datetime.now().isoformat(timespec="seconds"),
    }
    st.session_state.turns.append(turn)
    st.session_state.history.extend([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": result.get("assistant_text", "")},
    ])

    transcript = new_transcript(version, provider_name, model.strip() or None, artifact)
    transcript["turns"] = st.session_state.turns
    transcript_path = TRANSCRIPTS_DIR / f"{transcript['transcript_id']}.transcript.json"
    write_transcript(transcript_path, transcript)
    st.session_state.transcript_path = str(transcript_path)

    with st.chat_message("assistant"):
        if result.get("status") == "provider_error":
            st.error(result.get("assistant_text") or "Provider configuration error.")
        else:
            st.write(result.get("assistant_text") or "")
        st.caption(f"status={result.get('status', 'unknown')}")
        for event in result.get("tool_events", []):
            render_event(event)
        st.caption(f"Transcript: `{transcript_path}`")


if __name__ == "__main__":
    main()