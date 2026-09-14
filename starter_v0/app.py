"""
Streamlit Web Chat UI for Day 04 IT Helpdesk Agent.
Reuses `run_model_tool_loop` from `chat.py` for consistent evaluation & CLI behavior.
"""
from __future__ import annotations

import json
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version
from chat import run_model_tool_loop, trim_history

load_lab_env(ROOT)

st.set_page_config(
    page_title="Northstar Labs — IT Helpdesk Agent",
    page_icon="🛠️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1E88E5, #43A047);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-family: monospace;
        font-weight: 600;
        background-color: #f0f4f8;
        color: #2c3e50;
        border: 1px solid #dce4ec;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Cấu hình Agent")
    provider_name = st.selectbox(
        "Model Provider",
        options=["gemini", "openrouter", "openai", "anthropic"],
        index=0,
    )
    version_label = st.selectbox(
        "Artifact Version",
        options=["v0", "v1", "v2", "v3"],
        index=0,
    )
    model_override = st.text_input("Model Override (bỏ trống để dùng mặc định)", value="")
    model_arg = model_override.strip() or None
    history_window = st.slider("Context History Window (turns)", min_value=1, max_value=10, value=5)
    max_tool_rounds = st.slider("Max Tool Rounds", min_value=1, max_value=8, value=4)

    system_prompt_path = ROOT / "artifacts" / "system_prompt.md"
    tools_path = ROOT / "artifacts" / "tools.yaml"

    artifact_ver = build_artifact_version(version_label, system_prompt_path, tools_path)

    st.markdown("---")
    st.markdown(f"**Artifact Version Hash:**")
    st.markdown(f"<span class='badge'>{artifact_ver.artifact_version}</span>", unsafe_allow_html=True)

    if st.button("🧹 Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.tool_history = []
        st.rerun()

st.markdown("<div class='main-header'>🛠️ Northstar Labs IT Helpdesk</div>", unsafe_allow_html=True)
st.caption(f"Trợ lý hỗ trợ CNTT nội bộ • Đang chạy phiên bản: **{artifact_ver.artifact_version}**")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_history" not in st.session_state:
    st.session_state.tool_history = []

# Load system prompt and tool declarations
try:
    system_prompt_text = system_prompt_path.read_text(encoding="utf-8")
    tool_decls = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_decls)
    provider = make_provider(provider_name)
except Exception as e:
    st.error(f"Lỗi khởi tạo agent: {e}")
    st.stop()

# Display chat history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if idx < len(st.session_state.tool_history) and st.session_state.tool_history[idx]:
            events = st.session_state.tool_history[idx]
            with st.expander(f"🔍 Chi tiết {len(events)} lượt gọi Tool", expanded=False):
                for ev in events:
                    st.markdown(f"**Tool:** `{ev.get('tool')}`")
                    st.markdown("**Tham số (Arguments):**")
                    st.json(ev.get("args", {}))
                    st.markdown("**Kết quả trả về (Result):**")
                    st.json(ev.get("result", {}))
                    st.divider()

# User Input
if user_input := st.chat_input("Nhập yêu cầu hỗ trợ (ví dụ: 'Kiểm tra trạng thái VPN production')..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.tool_history.append([])
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare context
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
    trimmed = trim_history(history, history_window)
    working_messages = [{"role": "system", "content": system_prompt_text}]
    working_messages.extend(trimmed)
    working_messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý và thực thi công cụ..."):
            try:
                loop_result = run_model_tool_loop(
                    provider=provider,
                    messages=working_messages,
                    tools=openai_tools,
                    model=model_arg,
                    max_tool_rounds=max_tool_rounds,
                )
                assistant_text = loop_result.get("assistant_text", "")
                tool_events = loop_result.get("tool_events", [])
                st.markdown(assistant_text)

                if tool_events:
                    with st.expander(f"🔍 Chi tiết {len(tool_events)} lượt gọi Tool", expanded=True):
                        for ev in tool_events:
                            st.markdown(f"**Tool:** `{ev.get('tool')}`")
                            st.markdown("**Tham số (Arguments):**")
                            st.json(ev.get("args", {}))
                            st.markdown("**Kết quả trả về (Result):**")
                            st.json(ev.get("result", {}))
                            st.divider()

                st.session_state.messages.append({"role": "assistant", "content": assistant_text})
                st.session_state.tool_history.append(tool_events)
            except Exception as exc:
                err_msg = f"⚠️ Lỗi khi gọi agent: {exc}"
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
                st.session_state.tool_history.append([])
