from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import run_model_tool_loop, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
load_lab_env(ROOT)


# Streamlit Page Config
st.set_page_config(
    page_title="Northstar Labs — IT Helpdesk Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .stApp { background-color: #0f1f2e; color: #e8f0fb; }
    .main-header { font-size: 2.2rem; font-weight: 800; color: #4f9cf9; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1rem; color: #93b8e0; margin-bottom: 1.5rem; }
    .tool-box { background-color: #1e3a5a; border-left: 4px solid #4f9cf9; padding: 10px; border-radius: 6px; margin: 8px 0; font-family: monospace; font-size: 0.9rem; color: #93d4ff; }
    .metric-card { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.18); border-radius: 10px; padding: 12px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)


# Sidebar Configuration
st.sidebar.title("⚙️ Agent Controls")
version_label = st.sidebar.selectbox("Artifact Version", ["v3", "v2", "v1", "v0"], index=0)
provider_choice = st.sidebar.selectbox("Model Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
model_name = st.sidebar.text_input("Custom Model (optional)", value="")
history_window = st.sidebar.slider("History Window (turns)", 1, 10, 5)
max_tool_rounds = st.sidebar.slider("Max Tool Rounds", 1, 6, 4)

# Load System Prompt and Tools
system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"

system_prompt = system_prompt_path.read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(tools_path)
openai_tools = to_openai_tools(tool_declarations)
artifact_version = build_artifact_version(version_label, system_prompt_path, tools_path)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Artifact Version:** `{artifact_version.artifact_version}`")
st.sidebar.markdown(f"**Prompt Hash:** `{artifact_version.prompt_hash[:12]}`")
st.sidebar.markdown(f"**Tools Hash:** `{artifact_version.tools_hash[:12]}`")

# Initialize Chat State & Transcript ID
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

if "transcript_id" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    st.session_state.transcript_id = f"{version_label}_{provider_choice}_{timestamp}"

transcript_path = TRANSCRIPTS_DIR / f"{st.session_state.transcript_id}.transcript.json"
st.sidebar.markdown(f"**Transcript Path:**\n`{transcript_path.relative_to(ROOT)}`")

# Header Section
st.markdown('<div class="main-header">🛠️ Northstar Labs IT Helpdesk Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI Assistant with Structured Tool Calling, Context Carry-over & Safety Guardrails</div>', unsafe_allow_html=True)

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "tool_events" in msg and msg["tool_events"]:
            with st.expander("🔍 View Executed Tool Calls & Results"):
                for event in msg["tool_events"]:
                    st.markdown(f"**Tool:** `{event['tool']}`")
                    st.code(json.dumps(event['args'], ensure_ascii=False, indent=2), language="json")
                    st.markdown("**Result:**")
                    st.code(json.dumps(event['result'], ensure_ascii=False, indent=2), language="json")

# Handle User Input
if user_input := st.chat_input("Hỏi IT Helpdesk (ví dụ: 'Kiểm tra trạng thái VPN production', 'Mã tài sản LT-204')..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Prepare working messages
    recent_history = st.session_state.history[-history_window * 2:]
    messages = [
        {"role": "system", "content": system_prompt},
        *recent_history,
        {"role": "user", "content": user_input}
    ]

    with st.chat_message("assistant"):
        with st.spinner("Analyzing request and executing tools..."):
            try:
                # Instantiate Provider
                provider = make_provider(provider_choice)
                
                # Execute agent loop via chat.py's run_model_tool_loop
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model_name or None,
                    max_tool_rounds=max_tool_rounds
                )
                
                assistant_text = result["assistant_text"]
                st.write(assistant_text)
                
                if result.get("tool_events"):
                    with st.expander("🔍 View Executed Tool Calls & Results"):
                        for event in result["tool_events"]:
                            st.markdown(f"**Tool:** `{event['tool']}`")
                            st.code(json.dumps(event['args'], ensure_ascii=False, indent=2), language="json")
                            st.markdown("**Result:**")
                            st.code(json.dumps(event['result'], ensure_ascii=False, indent=2), language="json")
                
                # Save to history & chat state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_events": result.get("tool_events", [])
                })
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
                
            except Exception as exc:
                error_msg = f"❌ **Error during execution:** {type(exc).__name__}: {str(exc)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
