import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
import streamlit as st

# Đường dẫn thư mục gốc
ROOT = Path(__file__).resolve().parent.parent if (Path(__file__).resolve().parent.parent / "chat.py").exists() else Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Tái sử dụng trực tiếp từ chat.py và các module của repo
from chat import (
    run_model_tool_loop,
    trim_history,
    write_transcript,
    safe_slug,
    now_iso,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

# Nạp biến môi trường (.env)
load_lab_env(ROOT)

st.set_page_config(
    page_title="Streamlit Live Chat - IT Helpdesk",
    page_icon="🤖",
    layout="wide"
)

# ----------------- SIDEBAR -----------------
st.sidebar.title("⚙️ Cấu hình Agent")

provider_choices = ["groq", "openrouter", "openai", "anthropic", "gemini", "9router"]
default_provider_index = 0  # mặc định groq theo yêu cầu
selected_provider_name = st.sidebar.selectbox("Provider", provider_choices, index=default_provider_index)

# Khởi tạo provider để lấy default_model
try:
    active_provider = make_provider(selected_provider_name)
    default_model_name = getattr(active_provider, "default_model", "qwen/qwen3.8-27b")
except Exception as e:
    active_provider = None
    default_model_name = "qwen/qwen3.8-27b"

custom_model = st.sidebar.text_input("Model", value=default_model_name)
version_label = st.sidebar.text_input("Version Label", value="v3")
history_window = st.sidebar.number_input("History Window", min_value=1, max_value=20, value=5, step=1)
max_tool_rounds = st.sidebar.number_input("Max Tool Rounds", min_value=1, max_value=20, value=4, step=1)

# Nạp Artifacts & Hashes
system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"

st.sidebar.markdown("---")
st.sidebar.subheader("📦 Artifacts Meta")
try:
    artifact_version_info = build_artifact_version(version_label, system_prompt_path, tools_path)
    meta_dict = artifact_version_dict(artifact_version_info)
    st.sidebar.text(f"Artifact Ver: {meta_dict.get('artifact_version', 'N/A')}")
    st.sidebar.text(f"Prompt Hash:  {meta_dict.get('prompt_hash', 'N/A')[:12]}...")
    st.sidebar.text(f"Tools Hash:   {meta_dict.get('tools_hash', 'N/A')[:12]}...")
except Exception as e:
    st.sidebar.warning(f"Lỗi đọc artifact: {e}")
    meta_dict = {}

if st.sidebar.button("🧹 New conversation", use_container_width=True):
    st.session_state.history = []
    st.session_state.turns_display = []
    st.session_state.current_transcript = None
    st.session_state.transcript_path = None
    st.rerun()

# ----------------- SESSION STATE -----------------
if "history" not in st.session_state:
    st.session_state.history = []  # Lưu các turn [ {"role": "user"/"assistant", "content": "..."} ]
if "turns_display" not in st.session_state:
    st.session_state.turns_display = []  # Lưu dữ liệu hiển thị giao diện UI

# Khởi tạo đối tượng transcript đúng chuẩn format chat.py
if "current_transcript" not in st.session_state or st.session_state.current_transcript is None:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    t_id = "_".join([safe_slug(version_label), safe_slug(selected_provider_name), timestamp])
    t_path = ROOT / "transcripts" / f"{t_id}.transcript.json"
    st.session_state.transcript_path = t_path
    st.session_state.current_transcript = {
        "transcript_id": t_id,
        **meta_dict,
        "provider": selected_provider_name,
        "model": custom_model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": int(history_window),
        "max_tool_rounds": int(max_tool_rounds),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

st.title("🤖 IT Helpdesk Agent Chat")
st.caption(f"Provider: **{selected_provider_name}** | Model: **{custom_model}** | Version: **{version_label}**")

# ----------------- HELPER RENDER JSON -----------------
def render_assistant_reply(text: str):
    if not text:
        return
    parsed = None
    try:
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:].rstrip("`").strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:].rstrip("`").strip()
        parsed = json.loads(clean_text)
    except Exception:
        pass

    if isinstance(parsed, dict) and "reply" in parsed:
        st.info(f"**💬 Reply:** {parsed['reply']}")
        with st.expander("🔍 Xem Raw JSON Assistant", expanded=False):
            st.json(parsed)
    else:
        st.markdown(text)

# ----------------- RENDER LỊCH SỬ HỘI THOẠI -----------------
for turn in st.session_state.turns_display:
    with st.chat_message("user"):
        st.write(turn["user"])

    with st.chat_message("assistant"):
        # Status Badge
        st_val = turn.get("status", "answered")
        if st_val == "answered":
            st.success(f"Status: `{st_val}`")
        elif st_val == "waiting_for_user":
            st.warning(f"Status: `{st_val}`")
        elif st_val == "max_tool_rounds":
            st.warning(f"Status: `{st_val}`")
        elif st_val == "provider_error":
            st.error(f"Status: `{st_val}`")

        # Chi tiết từng Round và Tool calls/results
        rounds = turn.get("rounds", [])
        for r in rounds:
            r_idx = r.get("round", 1)
            tool_calls = r.get("tool_calls", [])
            tool_results = r.get("tool_results", [])

            for call in tool_calls:
                t_name = call.get("name")
                t_args = call.get("args")

                # Tìm kết quả tương ứng trong round
                matching_res = next((res for res in tool_results if res.get("tool") == t_name), None)
                
                with st.expander(f"🛠️ Round {r_idx}: `{t_name}`", expanded=False):
                    st.markdown("**Arguments:**")
                    st.json(t_args)
                    if matching_res:
                        st.markdown("**Result:**")
                        res_val = matching_res.get("result", {})
                        if isinstance(res_val, dict) and "error" in res_val:
                            st.error(f"Lỗi Tool: {res_val['error']} - {res_val.get('message', '')}")
                        st.json(res_val)

        # Hiển thị nội dung tin nhắn của Assistant
        render_assistant_reply(turn.get("assistant_text", ""))

if st.session_state.transcript_path:
    st.caption(f"📝 Transcript path: `{st.session_state.transcript_path}`")

# ----------------- XỬ LÝ INPUT CỦA USER -----------------
user_text = st.chat_input("Nhập tin nhắn...")

if user_text:
    # 1. Hiển thị prompt user ngay lập tức
    with st.chat_message("user"):
        st.write(user_text)

    # 2. Chuẩn bị tools và prompt
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    
    provider_inst = make_provider(selected_provider_name)
    
    # 3. Chuẩn bị messages theo trim_history
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, int(history_window)),
        {"role": "user", "content": user_text},
    ]

    turn_index = len(st.session_state.turns_display) + 1
    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            try:
                # Gọi ĐÚNG signature keyword-only của chat.py
                result = run_model_tool_loop(
                    provider=provider_inst,
                    messages=messages,
                    tools=openai_tools,
                    model=custom_model,
                    max_tool_rounds=int(max_tool_rounds),
                )
                turn_record.update(result)
                assistant_text = result.get("assistant_text", "")
                
                # Cập nhật lịch sử
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
                
            except Exception as exc:
                err_str = f"{type(exc).__name__}: {str(exc)}"
                # Không hiển thị/log API key
                if "api_key" in err_str.lower() or "authorization" in err_str.lower():
                    err_str = f"{type(exc).__name__}: [REDACTED_API_KEY_ERROR]"

                turn_record.update({
                    "status": "provider_error",
                    "error": err_str,
                    "assistant_text": f"Lỗi từ nhà cung cấp: {err_str}",
                })
                st.error(turn_record["error"])

            turn_record["ended_at"] = now_iso()

            # 4. Ghi transcript dùng write_transcript chuẩn của chat.py
            try:
                st.session_state.current_transcript["turns"].append(turn_record)
                write_transcript(st.session_state.transcript_path, st.session_state.current_transcript)
            except Exception as write_err:
                st.error(f"Lỗi ghi transcript: {write_err}")

            # 5. Lưu record vào danh sách hiển thị và refresh lại giao diện
            st.session_state.turns_display.append(turn_record)
            st.rerun()