from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
DEFAULT_SYSTEM_PROMPT = ARTIFACTS_DIR / "system_prompt.md"
DEFAULT_TOOLS = ARTIFACTS_DIR / "tools.yaml"
RUNS_DIR = ROOT / "runs"
PROVIDER_KEYS = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}
def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def json_block(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def display_reply(text: str | None) -> str:
    if not text:
        return ""
    stripped = text.strip()
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return text
    if isinstance(payload, dict) and isinstance(payload.get("reply"), str):
        return payload["reply"]
    return text


def provider_key_status(provider_name: str) -> tuple[str, bool]:
    key_name = PROVIDER_KEYS.get(provider_name, "")
    if not key_name:
        return "unknown provider", False
    return key_name, bool(os.getenv(key_name))


def default_provider_index(provider_names: list[str]) -> int:
    for preferred in ("openrouter", "openai", "anthropic", "gemini"):
        key_name = PROVIDER_KEYS[preferred]
        if os.getenv(key_name):
            return provider_names.index(preferred)
    return 0


def init_state() -> None:
    defaults = {
        "history": [],
        "turns": [],
        "transcript_path": None,
        "transcript_id": None,
        "last_config": None,
        "last_error": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_chat() -> None:
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.transcript_path = None
    st.session_state.transcript_id = None
    st.session_state.last_error = None


def read_artifacts(system_prompt_path: Path, tools_path: Path) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    return system_prompt, declarations, to_openai_tools(declarations)


def transcript_payload(
    *,
    transcript_id: str,
    artifact_version: Any,
    provider_name: str,
    model: str | None,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> dict[str, Any]:
    return {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "ui": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": st.session_state.turns,
    }


def ensure_transcript(
    *,
    version: str,
    provider_name: str,
    artifact_version: Any,
    model: str | None,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> Path:
    if st.session_state.transcript_path:
        return Path(st.session_state.transcript_path)

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "ui", timestamp])
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript_id = transcript_id
    st.session_state.transcript_path = str(path)
    payload = transcript_payload(
        transcript_id=transcript_id,
        artifact_version=artifact_version,
        provider_name=provider_name,
        model=model,
        system_prompt_path=system_prompt_path,
        tools_path=tools_path,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )
    write_transcript(path, payload)
    return path


def write_current_transcript(
    *,
    path: Path,
    artifact_version: Any,
    provider_name: str,
    model: str | None,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    transcript_id = st.session_state.transcript_id or path.stem.replace(".transcript", "")
    payload = transcript_payload(
        transcript_id=transcript_id,
        artifact_version=artifact_version,
        provider_name=provider_name,
        model=model,
        system_prompt_path=system_prompt_path,
        tools_path=tools_path,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )
    write_transcript(path, payload)


def render_tool_trace(turns: list[dict[str, Any]]) -> None:
    st.subheader("Tool trace")
    if not turns:
        st.caption("No interaction yet.")
        return

    latest = turns[-1]
    rounds = latest.get("rounds") or []
    if not rounds:
        st.caption("Latest turn did not call tools.")
        return

    for round_item in rounds:
        round_index = round_item.get("round", "?")
        calls = round_item.get("tool_calls") or []
        results = round_item.get("tool_results") or []
        title = f"Round {round_index}: {len(calls)} call(s)"
        with st.expander(title, expanded=False):
            assistant_text = round_item.get("assistant_text")
            if assistant_text:
                st.caption("Assistant draft")
                st.code(assistant_text, language="text")

            if not calls:
                st.caption("No tool calls in this round.")

            for index, call in enumerate(calls, start=1):
                name = call.get("name", "unknown")
                st.markdown(f"**{index}. `{name}`**")
                st.caption("Arguments")
                st.code(json_block(call.get("args", {})), language="json")

                if index <= len(results):
                    result = results[index - 1]
                    st.caption("Result")
                    st.code(json_block(result.get("result", result)), language="json")


def render_chat_history(history: list[dict[str, str]]) -> None:
    for message in history:
        role = "assistant" if message["role"] == "assistant" else "user"
        with st.chat_message(role):
            content = display_reply(message["content"]) if role == "assistant" else message["content"]
            st.markdown(content)


def run_turn(
    *,
    user_text: str,
    provider_name: str,
    model_override: str,
    version: str,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    st.session_state.last_error = None
    model = model_override.strip() or None
    system_prompt, _declarations, openai_tools = read_artifacts(system_prompt_path, tools_path)
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    provider = make_provider(provider_name)
    selected_model = model or getattr(provider, "default_model", None)
    transcript_path = ensure_transcript(
        version=version,
        provider_name=provider_name,
        artifact_version=artifact_version,
        model=selected_model,
        system_prompt_path=system_prompt_path,
        tools_path=tools_path,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )

    turn_index = len(st.session_state.turns) + 1
    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]

    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model,
            max_tool_rounds=max_tool_rounds,
        )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": assistant_text})
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        turn_record.update({
            "status": "provider_error",
            "error": message,
            "assistant_text": f"Provider error: {message}",
        })
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": turn_record["assistant_text"]})
        st.session_state.last_error = message

    turn_record["ended_at"] = now_iso()
    st.session_state.turns.append(turn_record)
    write_current_transcript(
        path=transcript_path,
        artifact_version=artifact_version,
        provider_name=provider_name,
        model=selected_model,
        system_prompt_path=system_prompt_path,
        tools_path=tools_path,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )


def main() -> None:
    load_lab_env(ROOT)
    st.set_page_config(page_title="IT Helpdesk Agent", page_icon=":material/support_agent:", layout="wide")
    init_state()

    st.markdown(
        """
        <style>
        :root {
          --ink: #172026;
          --muted: #5d6872;
          --line: #d6dde3;
          --panel: #eef3f6;
          --accent: #0f766e;
          --warn: #a16207;
          --code: #111827;
        }
        .stApp {
          background:
            linear-gradient(90deg, rgba(15,118,110,.08) 0 1px, transparent 1px 100%),
            linear-gradient(180deg, rgba(15,118,110,.06) 0 1px, transparent 1px 100%),
            #fbfcfd;
          background-size: 28px 28px;
          color: var(--ink);
        }
        .block-container {
          padding-top: 1.2rem;
          max-width: 1500px;
        }
        section[data-testid="stSidebar"] {
          background: #eef3f6;
          border-right: 1px solid var(--line);
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
          font-size: 1.1rem;
          letter-spacing: 0;
        }
        section[data-testid="stSidebar"] .stButton button {
          border-radius: 8px;
          border: 1px solid #b9c6cf;
          background: #ffffff;
          color: var(--ink);
        }
        .lab-title {
          border-left: 5px solid var(--accent);
          padding-left: 14px;
          margin-bottom: 8px;
        }
        .lab-title h1 {
          font-family: "Segoe UI", system-ui, sans-serif;
          font-size: 2rem;
          letter-spacing: 0;
          margin: 0;
        }
        .lab-title p {
          margin: 4px 0 0;
          color: var(--muted);
        }
        div[data-testid="stExpander"] {
          border: 1px solid var(--line);
          border-radius: 8px;
          background: rgba(255,255,255,.86);
        }
        code, pre {
          font-family: "Cascadia Mono", "SFMono-Regular", Consolas, monospace;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Helpdesk chat")
        st.caption("Chọn provider, nhập yêu cầu hỗ trợ, rồi xem tool trace ở màn hình chính.")
        provider_names = ["openrouter", "openai", "anthropic", "gemini"]
        provider_name = st.selectbox("Provider", provider_names, index=default_provider_index(provider_names))

        if st.button("New chat", width="stretch"):
            reset_chat()
            st.rerun()

        with st.expander("Advanced settings"):
            version = st.text_input("Artifact label", value="ui")
            model_override = st.text_input("Model override", value="")
            history_window = st.slider("History window", min_value=1, max_value=10, value=5)
            max_tool_rounds = st.slider("Max tool rounds", min_value=1, max_value=8, value=4)
            system_prompt_path = Path(st.text_input("System prompt path", value=str(DEFAULT_SYSTEM_PROMPT)))
            tools_path = Path(st.text_input("Tools YAML path", value=str(DEFAULT_TOOLS)))

        st.divider()
        st.markdown("**Demo prompts**")
        st.caption("VPN production có đang lỗi không?")
        st.caption("Kiểm tra VPN trên LT-204.")
        st.caption("Tạo ticket high cho lỗi VPN trên LT-204.")

    try:
        artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
        provider = make_provider(provider_name)
        selected_model = model_override.strip() or getattr(provider, "default_model", "")
    except Exception as exc:
        st.error(f"Configuration error: {type(exc).__name__}: {exc}")
        return

    st.markdown(
        """
        <div class="lab-title">
          <h1>IT Helpdesk Agent</h1>
          <p>Chat UI for tool routing, arguments, results, artifacts, and transcript evidence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.last_error:
        st.warning(st.session_state.last_error)

    chat_col, trace_col = st.columns([1.25, 1], gap="large")

    with chat_col:
        st.subheader("Chat")
        if not st.session_state.history:
            st.info("Send a helpdesk request to start a transcript.")
        render_chat_history(st.session_state.history)

    with trace_col:
        render_tool_trace(st.session_state.turns)

    user_text = st.chat_input("Ask about service status, assets, users, policy, KB articles, or ticket confirmation")
    if user_text:
        with st.spinner("Running agent loop and tools..."):
            run_turn(
                user_text=user_text,
                provider_name=provider_name,
                model_override=model_override,
                version=version,
                system_prompt_path=system_prompt_path,
                tools_path=tools_path,
                history_window=history_window,
                max_tool_rounds=max_tool_rounds,
            )
        st.rerun()


if __name__ == "__main__":
    main()
