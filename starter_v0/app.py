from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop, trim_history, safe_slug, now_iso, write_transcript

# Setup paths and environment
ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

# Streamlit Page Config
st.set_page_config(
    page_title="Northstar Labs — IT Helpdesk Agent",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .artifact-badge {
        display: inline-block;
        background-color: #EEF2FF;
        color: #4F46E5;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-family: monospace;
        font-weight: 600;
        border: 1px solid #C7D2FE;
    }
    .tool-badge {
        display: inline-block;
        background: #F1F5F9;
        color: #0F172A;
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-family: monospace;
        font-weight: 600;
        border: 1px solid #CBD5E1;
        margin-right: 0.3rem;
    }
    .tool-round-box {
        background: #F8FAFC;
        border-left: 3px solid #3B82F6;
        padding: 0.8rem;
        border-radius: 4px;
        margin-bottom: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar: Configuration and Artifact Audit
with st.sidebar:
    st.header("⚙️ Cấu hình Agent")

    provider_name = st.selectbox(
        "Model Provider",
        options=["gemini", "openai", "anthropic", "openrouter"],
        index=0,
        help="Chọn backend LLM hỗ trợ Function Calling",
    )

    version_label = st.selectbox(
        "Artifact Version",
        options=["v3", "v2", "v1", "v0"],
        index=0,
        help="Chọn nhãn phiên bản thử nghiệm",
    )

    model_override = st.text_input(
        "Model Name (Tùy chọn)",
        value="",
        placeholder="Để trống để dùng model mặc định",
    )

    history_window = st.slider("History Window (Turns)", min_value=1, max_value=10, value=5)
    max_tool_rounds = st.slider("Max Tool Rounds", min_value=1, max_value=6, value=4)

    st.markdown("---")
    st.header("📋 Artifact Info")

    # Load system prompt and tool declarations
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"

    system_prompt = system_prompt_path.read_text(encoding="utf-8") if system_prompt_path.exists() else ""
    tool_declarations = load_tool_declarations(tools_path) if tools_path.exists() else []
    openai_tools = to_openai_tools(tool_declarations)

    artifact_ver = build_artifact_version(version_label, system_prompt_path, tools_path)

    st.markdown(f"**Artifact Version:** <span class='artifact-badge'>{artifact_ver.artifact_version}</span>", unsafe_allow_html=True)
    st.caption(f"Prompt Hash: `{artifact_ver.prompt_hash[:16]}...`")
    st.caption(f"Tools Hash: `{artifact_ver.tools_hash[:16]}...`")

    with st.expander("👁️ Xem System Prompt"):
        st.markdown(f"```markdown\n{system_prompt}\n```")

    with st.expander(f"🛠️ Danh sách Tools ({len(tool_declarations)})"):
        for t in tool_declarations:
            st.markdown(f"- **`{t['name']}`**: {t.get('description', '')[:80]}...")

    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.transcript = None
        st.rerun()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "transcript" not in st.session_state or st.session_state.transcript is None:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        safe_slug(version_label),
        safe_slug(provider_name),
        timestamp,
    ])
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_ver),
        "provider": provider_name,
        "model": model_override or "default",
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

# Header
st.markdown("<div class='main-header'>🛠️ Northstar Labs — IT Helpdesk Agent</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='sub-header'>Hệ thống hỗ trợ sự cố nội bộ với Structured Tool Calling & Guardrails an toàn "
    f"| Phiên bản: <code>{artifact_ver.artifact_version}</code></div>",
    unsafe_allow_html=True,
)

# Render Chat History
for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role):
        if role == "assistant" and msg.get("rounds"):
            tool_rounds = msg["rounds"]
            has_tool_calls = any(r.get("tool_calls") for r in tool_rounds)
            if has_tool_calls:
                with st.expander("🔍 Chi tiết thực thi Tools (Audit Trail)", expanded=False):
                    for r in tool_rounds:
                        calls = r.get("tool_calls", [])
                        results = r.get("tool_results", [])
                        if calls:
                            st.markdown(f"**Vòng lặp {r.get('round', 1)}:**")
                            for idx, call in enumerate(calls):
                                st.markdown(f"<span class='tool-badge'>🔧 {call['name']}</span>", unsafe_allow_html=True)
                                st.json(call.get("args", {}), expanded=False)
                                if idx < len(results):
                                    res = results[idx].get("result", {})
                                    if isinstance(res, dict) and "error" in res:
                                        st.error(f"Lỗi: {res['error']} - {res.get('message', '')}")
                                    else:
                                        st.success("Kết quả tool:")
                                        st.json(res, expanded=False)
        st.markdown(msg["content"])

# Suggestion Chips if no messages yet
if not st.session_state.messages:
    st.info("💡 **Gợi ý yêu cầu nhanh:** Hãy thử nhấp vào một trong các câu hỏi dưới đây hoặc tự gõ câu hỏi của bạn.")
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("Kiểm tra VPN Production", use_container_width=True):
        st.session_state.prompt_input = "Kiểm tra trạng thái dịch vụ VPN production giúp mình."
    if col2.button("Kiểm tra laptop của tôi", use_container_width=True):
        st.session_state.prompt_input = "Kiểm tra giúp mình chiếc laptop cá nhân của mình."
    if col3.button("Tạo ticket lỗi mạng LT-204", use_container_width=True):
        st.session_state.prompt_input = "Tạo ticket mức high cho lỗi VPN trên LT-204 giúp mình."
    if col4.button("Hỏi chính sách mật khẩu", use_container_width=True):
        st.session_state.prompt_input = "Chính sách công ty có cho phép lưu mật khẩu vào ticket không?"

# Chat Input Handler
user_query = st.chat_input("Nhập câu hỏi hoặc sự cố kỹ thuật cần hỗ trợ...")
if "prompt_input" in st.session_state and st.session_state.prompt_input:
    user_query = st.session_state.prompt_input
    st.session_state.prompt_input = None

if user_query:
    # Append User Message to State
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Build conversation context
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]
    trimmed = trim_history(chat_history, history_window)
    working_messages = [
        {"role": "system", "content": system_prompt},
        *trimmed,
        {"role": "user", "content": user_query},
    ]

    # Run Agent Loop
    with st.chat_message("assistant"):
        with st.spinner("Đang phân tích và gọi công cụ..."):
            try:
                provider = make_provider(provider_name)
                turn_index = len(st.session_state.transcript["turns"]) + 1
                turn_record = {
                    "turn_index": turn_index,
                    "started_at": now_iso(),
                    "user": user_query,
                    "status": "started",
                    "assistant_text": None,
                    "rounds": [],
                    "tool_events": [],
                }

                result = run_model_tool_loop(
                    provider=provider,
                    messages=working_messages,
                    tools=openai_tools,
                    model=model_override or None,
                    max_tool_rounds=max_tool_rounds,
                )

                turn_record.update(result)
                turn_record["ended_at"] = now_iso()
                st.session_state.transcript["turns"].append(turn_record)
                write_transcript(st.session_state.transcript_path, st.session_state.transcript)

                assistant_reply = result.get("assistant_text", "")
                rounds = result.get("rounds", [])

                # Render Tools Inspector
                has_tool_calls = any(r.get("tool_calls") for r in rounds)
                if has_tool_calls:
                    with st.expander("🔍 Chi tiết thực thi Tools (Audit Trail)", expanded=True):
                        for r in rounds:
                            calls = r.get("tool_calls", [])
                            results = r.get("tool_results", [])
                            if calls:
                                st.markdown(f"**Vòng lặp {r.get('round', 1)}:**")
                                for idx, call in enumerate(calls):
                                    st.markdown(f"<span class='tool-badge'>🔧 {call['name']}</span>", unsafe_allow_html=True)
                                    st.json(call.get("args", {}), expanded=False)
                                    if idx < len(results):
                                        res = results[idx].get("result", {})
                                        if isinstance(res, dict) and "error" in res:
                                            st.error(f"Lỗi: {res['error']} - {res.get('message', '')}")
                                        else:
                                            st.success("Kết quả tool:")
                                            st.json(res, expanded=False)

                st.markdown(assistant_reply)

                # Save Assistant Message to State
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_reply,
                    "rounds": rounds,
                })

            except Exception as exc:
                err_msg = f"Đã xảy ra lỗi khi gọi Provider: {type(exc).__name__}: {str(exc)}"
                st.error(err_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": err_msg,
                    "rounds": [],
                })

# Sidebar download button for transcript
with st.sidebar:
    if st.session_state.transcript and st.session_state.transcript.get("turns"):
        st.markdown("---")
        transcript_json_str = json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 Tải xuống Transcript JSON",
            data=transcript_json_str,
            file_name=st.session_state.transcript_path.name,
            mime="application/json",
            use_container_width=True,
        )
