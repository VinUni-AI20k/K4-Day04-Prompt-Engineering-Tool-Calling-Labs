from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import (
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"

st.set_page_config(page_title="Northstar Helpdesk", page_icon="🛠️", layout="centered")

STATUS_LABELS = {
    "answered": "answered",
    "waiting_for_user": "waiting for you",
    "max_tool_rounds": "stopped: max tool rounds",
    "provider_error": "provider error",
}

EXAMPLE_PROMPTS = [
    ("🔌", "Kiểm tra VPN production", "Kiểm tra VPN production đang lỗi gì không?"),
    ("👤", "Tra cứu nhân viên", "Tra cứu tài khoản nhân viên EMP-1007 và thiết bị được cấp."),
    ("📄", "Tìm hướng dẫn", "Tìm hướng dẫn cấu hình Outlook profile trên Windows 11."),
    ("🧾", "Tạo ticket", "Laptop LT-204 của tôi bị lỗi Wi-Fi liên tục, giúp mình xem tình trạng máy."),
]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

#MainMenu, footer, [data-testid="stHeader"] { visibility: hidden; height: 0; }

[data-testid="stMainBlockContainer"] {
  max-width: 780px;
  padding-top: 1.5rem;
  padding-bottom: 7rem;
}

.app-header { text-align: center; margin-bottom: 1.75rem; }
.app-header .title { font-size: 1.6rem; font-weight: 700; color: #1C1917; margin: 0; }
.app-header .subtitle { font-size: 0.92rem; color: #78716C; margin-top: 4px; }

[data-testid="stChatMessage"] { padding: 3px 0; }

[data-testid="stChatMessageContent"] {
  border-radius: 18px !important;
  padding: 11px 16px !important;
  line-height: 1.55;
  font-size: 0.95rem;
}

[data-testid="stChatMessageContent"][aria-label="Chat message from user"] {
  background: linear-gradient(135deg, #4F46E5, #6366F1);
}
[data-testid="stChatMessageContent"][aria-label="Chat message from user"] * {
  color: #ffffff !important;
}

[data-testid="stChatMessageContent"][aria-label="Chat message from assistant"] {
  background: #F5F5F4;
  border: 1px solid #E7E5E4;
  color: #1C1917;
}

.status-pill {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  padding: 2px 10px;
  border-radius: 999px;
  margin: 6px 0 0 2px;
}
.status-answered { background: #DCFCE7; color: #166534; }
.status-waiting_for_user { background: #FEF3C7; color: #92400E; }
.status-max_tool_rounds, .status-provider_error { background: #FEE2E2; color: #991B1B; }

[data-testid="stExpander"] {
  border-radius: 12px !important;
  border: 1px solid #E7E5E4 !important;
  margin-top: 6px;
}

[data-testid="stChatInput"] textarea { border-radius: 14px !important; }
[data-testid="stChatInput"] { max-width: 780px; margin: 0 auto; }

[data-testid="stSidebar"] { background: #FAFAF9; border-right: 1px solid #EDEBE8; }
[data-testid="stSidebar"] h2 { font-size: 1.05rem; }

[data-testid="stButton"] button {
  border-radius: 10px !important;
}

.suggestion-grid [data-testid="stButton"] button {
  text-align: left !important;
  padding: 0.9rem 1rem !important;
  border: 1px solid #E7E5E4 !important;
  background: #ffffff !important;
  height: auto;
  white-space: normal;
}
.suggestion-grid [data-testid="stButton"] button:hover {
  border-color: #6366F1 !important;
  color: #4F46E5 !important;
}
</style>
"""


def init_state() -> None:
    st.session_state.setdefault("turns", [])
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("transcript", None)
    st.session_state.setdefault("transcript_path", None)
    st.session_state.setdefault("pending_prompt", None)


def reset_conversation() -> None:
    st.session_state["turns"] = []
    st.session_state["history"] = []
    st.session_state["transcript"] = None
    st.session_state["transcript_path"] = None
    st.session_state["pending_prompt"] = None


def build_transcript(version: str, provider_name: str, model: str | None,
                      system_prompt_path: Path, tools_path: Path) -> tuple[dict, Path]:
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "ui", timestamp])
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        "version": artifact_version.version,
        "artifact_version": artifact_version.artifact_version,
        "prompt_hash": artifact_version.prompt_hash,
        "tools_hash": artifact_version.tools_hash,
        "provider": provider_name,
        "model": model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, path


st.markdown(CSS, unsafe_allow_html=True)
init_state()

with st.sidebar:
    st.header("⚙️ Cấu hình agent")
    provider_name = st.selectbox("Provider", ["openai", "openrouter", "anthropic", "gemini"], index=0)
    model_override = st.text_input("Model (để trống dùng default)", value="")
    version_label = st.text_input("Artifact version label", value="v_ui_demo")
    with st.expander("Nâng cao"):
        history_window = st.slider("History window", 1, 10, 5)
        max_tool_rounds = st.slider("Max tool rounds", 1, 8, 4)

    st.divider()
    st.caption(f"📄 system_prompt: `{(ARTIFACTS_DIR / 'system_prompt.md').name}`")
    st.caption(f"🔧 tools: `{(ARTIFACTS_DIR / 'tools.yaml').name}`")

    if st.button("↺ Reset hội thoại", use_container_width=True):
        reset_conversation()
        st.rerun()

    try:
        artifact_version = build_artifact_version(
            version_label, ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml"
        )
        st.divider()
        st.caption("Artifact version")
        st.code(artifact_version.artifact_version, language="text")
        st.caption(f"prompt_hash: {artifact_version.prompt_hash[:16]}…")
        st.caption(f"tools_hash: {artifact_version.tools_hash[:16]}…")
    except FileNotFoundError as exc:
        st.error(f"Không tìm thấy artifact: {exc}")
        artifact_version = None

    if st.session_state["transcript_path"]:
        st.divider()
        st.caption("📝 Transcript")
        st.code(str(st.session_state["transcript_path"]), language="text")


st.markdown(
    """
    <div class="app-header">
      <p class="title">🛠️ Northstar Labs IT Helpdesk</p>
      <p class="subtitle">Demo agent cho lab prompt engineering &amp; tool calling</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state["turns"]:
    st.markdown("<div class='suggestion-grid'>", unsafe_allow_html=True)
    cols = st.columns(2)
    for idx, (icon, label, prompt) in enumerate(EXAMPLE_PROMPTS):
        with cols[idx % 2]:
            if st.button(f"{icon}  {label}", key=f"example_{idx}", use_container_width=True):
                st.session_state["pending_prompt"] = prompt
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

for turn in st.session_state["turns"]:
    with st.chat_message("user", avatar="🧑‍💻"):
        st.write(turn["user"])
    with st.chat_message("assistant", avatar="🛠️"):
        st.write(turn["assistant_text"])
        status = turn.get("status", "unknown")
        st.markdown(
            f"<span class='status-pill status-{status}'>{STATUS_LABELS.get(status, status)}</span>",
            unsafe_allow_html=True,
        )

        for round_record in turn.get("rounds", []):
            calls = round_record.get("tool_calls") or []
            if not calls:
                continue
            with st.expander(f"🔧 Round {round_record['round']} — {len(calls)} tool call(s)"):
                for call, result in zip(calls, round_record.get("tool_results", [])):
                    st.markdown(f"**Tool:** `{call['name']}`")
                    st.markdown("Args:")
                    st.json(call["args"])
                    tool_result = result.get("result") if isinstance(result, dict) else result
                    if isinstance(tool_result, dict) and tool_result.get("error"):
                        st.error(f"error: {tool_result.get('error')} — {tool_result.get('message', '')}")
                    else:
                        st.markdown("Result:")
                        st.json(tool_result)
                    st.markdown("---")

typed_input = st.chat_input("Nhập yêu cầu IT helpdesk...")
user_text = typed_input or st.session_state.pop("pending_prompt", None)

if user_text:
    if artifact_version is None:
        st.error("Không thể chạy agent vì thiếu artifact (system_prompt.md hoặc tools.yaml).")
        st.stop()

    if st.session_state["transcript"] is None:
        transcript, path = build_transcript(
            version_label, provider_name, model_override or None,
            ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml",
        )
        st.session_state["transcript"] = transcript
        st.session_state["transcript_path"] = path

    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    openai_tools = to_openai_tools(tool_declarations)

    try:
        provider = make_provider(provider_name)
    except Exception as exc:
        st.error(f"Không khởi tạo được provider '{provider_name}': {exc}")
        st.stop()

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state["history"], history_window),
        {"role": "user", "content": user_text},
    ]

    turn_record = {
        "turn_index": len(st.session_state["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.spinner("Agent đang xử lý..."):
        try:
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=model_override or None,
                max_tool_rounds=max_tool_rounds,
            )
            turn_record.update(result)
            assistant_text = result["assistant_text"]
            st.session_state["history"].append({"role": "user", "content": user_text})
            st.session_state["history"].append({"role": "assistant", "content": assistant_text})
        except Exception as exc:
            turn_record.update({
                "status": "provider_error",
                "assistant_text": f"Lỗi provider: {type(exc).__name__}: {exc}",
                "error": f"{type(exc).__name__}: {exc}",
            })

    turn_record["ended_at"] = now_iso()
    st.session_state["turns"].append(turn_record)

    st.session_state["transcript"]["turns"].append(turn_record)
    write_transcript(st.session_state["transcript_path"], st.session_state["transcript"])

    st.rerun()
