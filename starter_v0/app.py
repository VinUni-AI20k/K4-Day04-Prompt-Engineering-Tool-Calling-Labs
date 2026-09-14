from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import build_turn_history, run_model_tool_loop, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"


def json_block(value: Any) -> None:
    st.code(json.dumps(value, ensure_ascii=False, indent=2, default=str), language="json")


def reset_chat() -> None:
    st.session_state.turns = []


def save_transcript(metadata: dict[str, str], provider_name: str, model: str | None) -> Path:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    path = TRANSCRIPTS_DIR / f"{metadata['version']}_{provider_name}_{timestamp}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": path.stem,
        **metadata,
        "provider": provider_name,
        "model": model,
        "system_prompt": "artifacts/system_prompt.md",
        "tools": "artifacts/tools.yaml",
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "turns": st.session_state.turns,
    }
    write_transcript(path, transcript)
    return path


def show_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.write(turn["user"])
    with st.chat_message("assistant"):
        st.write(turn["assistant_text"])
        for round_record in turn["rounds"]:
            with st.expander(f"Round {round_record['round']} tool trace"):
                json_block({
                    "tool_calls": round_record["tool_calls"],
                    "tool_results": round_record["tool_results"],
                    "final_response_validation": round_record.get("final_response_validation"),
                })


def main() -> None:
    st.set_page_config(page_title="Northstar Helpdesk Agent", page_icon="🛠️", layout="wide")
    st.title("Northstar Helpdesk Agent")
    st.caption("Lab UI: one shared model-tool loop, visible tool traces, and versioned transcripts.")

    if "turns" not in st.session_state:
        reset_chat()

    with st.sidebar:
        st.header("Run configuration")
        provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
        model = st.text_input("Model override (optional)") or None
        version = st.text_input("Artifact label", value="v3")
        if st.button("Start a new chat"):
            reset_chat()
            st.rerun()

    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact = build_artifact_version(version, prompt_path, tools_path)
    metadata = artifact_version_dict(artifact)
    st.sidebar.code(
        f"artifact_version\n{artifact.artifact_version}\n\nprompt_hash\n{artifact.prompt_hash}\n\ntools_hash\n{artifact.tools_hash}\n\ncontent_hash\n{artifact.content_hash}",
        language=None,
    )

    for turn in st.session_state.turns:
        show_turn(turn)

    user_text = st.chat_input("Describe an IT helpdesk request")
    if not user_text:
        return

    with st.chat_message("user"):
        st.write(user_text)

    system_prompt = prompt_path.read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(tools_path))
    messages = [
        {"role": "system", "content": system_prompt},
        *build_turn_history(st.session_state.turns, window=5),
        {"role": "user", "content": user_text},
    ]
    turn: dict[str, Any] = {"user": user_text, "assistant_text": "", "status": "provider_error", "rounds": []}

    with st.chat_message("assistant"):
        try:
            provider = make_provider(provider_name)
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=tools,
                model=model,
                max_tool_rounds=4,
            )
            turn.update(result)
            st.write(result["assistant_text"])
            for round_record in result["rounds"]:
                with st.expander(f"Round {round_record['round']} tool trace"):
                    json_block({
                        "tool_calls": round_record["tool_calls"],
                        "tool_results": round_record["tool_results"],
                        "final_response_validation": round_record.get("final_response_validation"),
                    })
        except Exception as exc:
            turn["error"] = f"{type(exc).__name__}: {exc}"
            st.error(f"Provider error: {turn['error']}")

    st.session_state.turns.append(turn)
    transcript_path = save_transcript(metadata, provider_name, model)
    st.caption(f"Transcript saved locally: {transcript_path}")


if __name__ == "__main__":
    main()
