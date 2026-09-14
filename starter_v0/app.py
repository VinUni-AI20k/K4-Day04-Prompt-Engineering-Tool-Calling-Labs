from __future__ import annotations

import json
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
load_lab_env(ROOT)


st.set_page_config(page_title="Northstar IT Helpdesk", page_icon="IT", layout="wide")
st.title("Northstar IT Helpdesk")
st.caption("Tool-calling demo with auditable local tool traces")

with st.sidebar:
    st.header("Session")
    provider_name = st.selectbox("Provider", ["gemini", "openrouter", "openai", "anthropic"])
    version = st.text_input("Artifact version", value="v1")
    model = st.text_input("Model override (optional)", value="")
    max_rounds = st.number_input("Maximum tool rounds", min_value=1, max_value=8, value=4)
    st.divider()
    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact_version = build_artifact_version(version, prompt_path, tools_path)
    st.caption(f"Artifact: {artifact_version.artifact_version}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("events"):
            with st.expander("Tool trace"):
                st.json(message["events"])

user_text = st.chat_input("Describe your IT helpdesk request")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    system_prompt = prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(declarations)
    history = [
        {"role": item["role"], "content": item["content"]}
        for item in st.session_state.messages[:-1]
        if item["role"] in {"user", "assistant"}
    ]
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_text},
    ]

    with st.chat_message("assistant"):
        try:
            provider = make_provider(provider_name)
            selected_model = model or getattr(provider, "default_model", None)
            result: dict[str, Any] = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=selected_model,
                max_tool_rounds=int(max_rounds),
            )
            assistant_text = result.get("assistant_text") or "No response returned."
            st.markdown(assistant_text)
            events = result.get("tool_events") or []
            if events:
                with st.expander("Tool trace", expanded=True):
                    for event in events:
                        st.write(f"**{event.get('tool')}**")
                        st.json({"args": event.get("args"), "result": event.get("result")})
            st.caption(f"Status: {result.get('status')} | Artifact: {artifact_version.artifact_version}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_text,
                "events": events,
            })
        except Exception as exc:
            error_text = f"Provider error: {type(exc).__name__}: {exc}"
            st.error(error_text)
            st.session_state.messages.append({"role": "assistant", "content": error_text, "events": []})

with st.sidebar:
    st.divider()
    st.subheader("Artifact hashes")
    st.json(artifact_version_dict(artifact_version))
    st.download_button(
        "Download session JSON",
        data=json.dumps(st.session_state.messages, ensure_ascii=False, indent=2),
        file_name="helpdesk-session.json",
        mime="application/json",
    )
