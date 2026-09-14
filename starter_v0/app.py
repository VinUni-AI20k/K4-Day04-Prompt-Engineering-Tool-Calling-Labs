from __future__ import annotations

import json
import os
from html import escape
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"

PROVIDERS = ("openrouter", "openai", "anthropic", "gemini")
PROVIDER_API_KEYS = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

QUICK_PROMPTS = (
    ("📡 VPN status", "Kiểm tra trạng thái VPN production."),
    ("💻 Device check", "Kiểm tra tình trạng hardware của thiết bị LT-204."),
    ("🧭 Missing info", "Kiểm tra giúp tôi tình trạng chiếc laptop đang dùng."),
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #172033;
            --muted: #62708a;
            --line: rgba(86, 103, 135, 0.16);
            --brand: #4f46e5;
            --brand-deep: #3730a3;
            --mint: #0f9f78;
            --panel: rgba(255, 255, 255, 0.82);
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 8% 2%, rgba(99, 102, 241, 0.13), transparent 31rem),
                radial-gradient(circle at 92% 12%, rgba(16, 185, 129, 0.10), transparent 27rem),
                #f7f9fc;
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1120px;
            padding-top: 2.1rem;
            padding-bottom: 5rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111827 0%, #18233a 58%, #172033 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
            color: #edf2ff;
        }

        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
            color: #aebbd2;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.12);
        }

        [data-testid="stSidebar"] .stButton button,
        [data-testid="stSidebar"] .stDownloadButton button {
            background: rgba(255, 255, 255, 0.09);
            border: 1px solid rgba(255, 255, 255, 0.16);
            color: #ffffff;
        }

        [data-testid="stSidebar"] .stButton button:hover,
        [data-testid="stSidebar"] .stDownloadButton button:hover {
            background: rgba(255, 255, 255, 0.16);
            border-color: rgba(255, 255, 255, 0.30);
        }

        .helpdesk-hero {
            position: relative;
            overflow: hidden;
            padding: 2rem 2.1rem;
            margin-bottom: 1.35rem;
            border: 1px solid rgba(99, 102, 241, 0.18);
            border-radius: 24px;
            background: linear-gradient(125deg, rgba(255,255,255,0.96), rgba(242,245,255,0.90));
            box-shadow: 0 18px 55px rgba(47, 56, 91, 0.10);
        }

        .helpdesk-hero::after {
            content: "";
            position: absolute;
            width: 210px;
            height: 210px;
            right: -70px;
            top: -105px;
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(99,102,241,.24), rgba(16,185,129,.18));
        }

        .hero-eyebrow {
            margin-bottom: .55rem;
            color: var(--brand);
            font-size: .74rem;
            font-weight: 800;
            letter-spacing: .13em;
            text-transform: uppercase;
        }

        .helpdesk-hero h1 {
            position: relative;
            z-index: 1;
            margin: 0;
            color: #182038;
            font-size: clamp(1.85rem, 4vw, 2.75rem);
            line-height: 1.08;
            letter-spacing: -0.045em;
        }

        .helpdesk-hero p {
            position: relative;
            z-index: 1;
            max-width: 700px;
            margin: .75rem 0 1.1rem;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.65;
        }

        .hero-pills {
            position: relative;
            z-index: 1;
            display: flex;
            flex-wrap: wrap;
            gap: .5rem;
        }

        .hero-pill {
            padding: .38rem .68rem;
            border: 1px solid rgba(79,70,229,.15);
            border-radius: 999px;
            background: rgba(255,255,255,.72);
            color: #46516a;
            font-size: .77rem;
            font-weight: 650;
        }

        .session-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .75rem;
            margin: .25rem 0 1.25rem;
        }

        .session-card {
            padding: .85rem 1rem;
            border: 1px solid var(--line);
            border-radius: 14px;
            background: var(--panel);
            box-shadow: 0 8px 24px rgba(45, 55, 90, .055);
        }

        .session-card span {
            display: block;
            margin-bottom: .25rem;
            color: #77839a;
            font-size: .67rem;
            font-weight: 750;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .session-card strong {
            display: block;
            overflow: hidden;
            color: #25304a;
            font-size: .88rem;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        [data-testid="stChatMessage"] {
            margin: .65rem 0;
            padding: 1rem 1.05rem;
            border: 1px solid var(--line);
            border-radius: 18px;
            background: rgba(255,255,255,.84);
            box-shadow: 0 8px 28px rgba(45,55,90,.055);
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: linear-gradient(135deg, rgba(238,242,255,.94), rgba(245,247,255,.92));
            border-color: rgba(99,102,241,.18);
        }

        [data-testid="stChatMessageContent"],
        [data-testid="stChatMessageContent"] p,
        [data-testid="stChatMessageContent"] li,
        [data-testid="stChatMessageContent"] strong {
            color: #263149 !important;
        }

        [data-testid="stChatMessageContent"] [data-testid="stJson"] {
            padding: .45rem .6rem;
            border-radius: 10px;
            background: #f8faff;
        }

        [data-testid="stChatMessageContent"] [data-testid="stJson"] * {
            color: #34415d !important;
        }

        [data-testid="stChatMessageContent"] [data-testid="stJson"] .react-json-view {
            background: #f8faff !important;
        }

        [data-testid="stChatMessageAvatarUser"] {
            background: linear-gradient(135deg, #6366f1, #4338ca) !important;
            color: #ffffff !important;
        }

        [data-testid="stChatMessageAvatarAssistant"] {
            background: linear-gradient(135deg, #14b88a, #087d62) !important;
            color: #ffffff !important;
        }

        [data-testid="stChatMessageAvatarUser"] *,
        [data-testid="stChatMessageAvatarAssistant"] * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }

        [data-testid="stChatInput"] {
            border: 1px solid rgba(79,70,229,.18);
            border-radius: 16px;
            background: rgba(255,255,255,.95);
            box-shadow: 0 10px 32px rgba(45,55,90,.10);
        }

        [data-testid="stChatInput"] > div {
            background: #ffffff !important;
        }

        [data-testid="stChatInputTextArea"] {
            color: #263149 !important;
            caret-color: var(--brand) !important;
        }

        [data-testid="stChatInputTextArea"]::placeholder {
            color: #8a95a9 !important;
            opacity: 1;
        }

        [data-testid="stChatInput"] button {
            color: var(--brand) !important;
        }

        [data-testid="stExpander"] {
            margin-top: .65rem;
            border: 1px solid rgba(79,70,229,.13);
            border-radius: 13px;
            background: rgba(248,250,255,.86);
        }

        [data-testid="stExpander"] summary {
            background: transparent !important;
            color: #33405b !important;
        }

        [data-testid="stExpander"] summary * {
            color: #33405b !important;
        }

        /* Keep the advanced settings visually inside the dark sidebar.
           Streamlit otherwise gives the expanded body a light surface while
           inheriting the sidebar's light text, which reduces readability. */
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, .22);
            background: rgba(8, 15, 29, .46);
            box-shadow: 0 10px 28px rgba(0, 0, 0, .12);
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            background: rgba(255, 255, 255, .055) !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
            background: rgba(255, 255, 255, .09) !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] summary,
        [data-testid="stSidebar"] [data-testid="stExpander"] summary * {
            color: #f8fafc !important;
            fill: #f8fafc !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
            padding-top: .45rem;
            background: rgba(8, 15, 29, .20);
        }

        [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {
            color: #dbe5f3 !important;
            font-weight: 650;
        }

        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] svg {
            color: #a9b8cd !important;
        }

        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div,
        [data-testid="stSidebar"] [data-baseweb="base-input"],
        [data-testid="stSidebar"] [data-testid="stTextInputRootElement"],
        [data-testid="stSidebar"] [data-testid="stNumberInputContainer"],
        [data-testid="stSidebar"] [data-testid="stSelectbox"] .react-aria-ComboBox > div {
            border-color: rgba(148, 163, 184, .28) !important;
            background: #0b1220 !important;
            color: #f8fafc !important;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] span,
        [data-testid="stSidebar"] [data-baseweb="select"] div {
            color: #f8fafc !important;
            -webkit-text-fill-color: #f8fafc !important;
        }

        [data-testid="stSidebar"] input::placeholder {
            color: #8291a8 !important;
            -webkit-text-fill-color: #8291a8 !important;
            opacity: 1;
        }

        [data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within,
        [data-testid="stSidebar"] [data-baseweb="input"] > div:focus-within,
        [data-testid="stSidebar"] [data-baseweb="base-input"]:focus-within,
        [data-testid="stSidebar"] [data-testid="stTextInputRootElement"]:focus-within,
        [data-testid="stSidebar"] [data-testid="stNumberInputContainer"]:focus-within,
        [data-testid="stSidebar"] [data-testid="stSelectbox"] .react-aria-ComboBox > div:focus-within {
            border-color: #818cf8 !important;
            box-shadow: 0 0 0 2px rgba(129, 140, 248, .22) !important;
        }

        [data-testid="stTabs"] [data-baseweb="tab-list"],
        [data-testid="stTabs"] [role="tablist"] {
            gap: .45rem;
            padding: .35rem;
            border: 1px solid var(--line);
            border-radius: 15px;
            background: rgba(255,255,255,.70);
        }

        [data-testid="stTabs"] [data-baseweb="tab"],
        [data-testid="stTabs"] [data-testid="stTab"] {
            min-height: 2.7rem;
            padding: .55rem 1rem;
            border-radius: 11px;
            color: #647089;
            font-weight: 700;
        }

        [data-testid="stTabs"] [data-baseweb="tab"] *,
        [data-testid="stTabs"] [data-testid="stTab"] * {
            color: #647089 !important;
        }

        [data-testid="stTabs"] [aria-selected="true"] {
            background: #ffffff;
            color: var(--brand-deep) !important;
            box-shadow: 0 5px 16px rgba(45,55,90,.09);
        }

        [data-testid="stTabs"] [aria-selected="true"] * {
            color: var(--brand-deep) !important;
        }

        [data-testid="stTabs"] .react-aria-SelectionIndicator {
            background: var(--brand) !important;
        }

        .trace-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: .5rem;
            margin-top: .65rem;
            color: #748097;
            font-size: .76rem;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: .28rem .58rem;
            border-radius: 999px;
            font-size: .7rem;
            font-weight: 800;
            letter-spacing: .035em;
            text-transform: uppercase;
        }

        .status-ok { background: #dcfce7; color: #166534; }
        .status-wait { background: #fef3c7; color: #92400e; }
        .status-error { background: #fee2e2; color: #991b1b; }
        .status-neutral { background: #e8ecf5; color: #475569; }

        .empty-state {
            padding: 1.35rem 1.45rem;
            margin: .35rem 0 1rem;
            border: 1px dashed rgba(79,70,229,.25);
            border-radius: 18px;
            background: rgba(255,255,255,.58);
            text-align: center;
        }

        .empty-state h3 {
            margin: 0 0 .35rem;
            color: #28324a;
            font-size: 1rem;
        }

        .empty-state p {
            margin: 0;
            color: #748097;
            font-size: .88rem;
        }

        .stButton button {
            border-radius: 12px;
            border-color: rgba(79,70,229,.16);
            transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
        }

        .stButton button:hover {
            border-color: rgba(79,70,229,.48);
            box-shadow: 0 7px 20px rgba(79,70,229,.10);
            transform: translateY(-1px);
        }

        [data-testid="stMainBlockContainer"] .stButton button {
            background: rgba(255,255,255,.94) !important;
            border-color: rgba(79,70,229,.17) !important;
            color: #33405b !important;
        }

        [data-testid="stMainBlockContainer"] .stButton button * {
            color: #33405b !important;
        }

        [data-testid="stMainBlockContainer"] .stButton button:hover {
            background: #ffffff !important;
            border-color: rgba(79,70,229,.50) !important;
            color: var(--brand-deep) !important;
        }

        @media (max-width: 700px) {
            [data-testid="stMainBlockContainer"] { padding-top: 1rem; }
            .helpdesk-hero { padding: 1.45rem 1.25rem; border-radius: 19px; }
            .session-strip { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session() -> None:
    defaults: dict[str, Any] = {
        "history": [],
        "turns": [],
        "transcript": None,
        "transcript_path": None,
        "session_config": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_conversation() -> None:
    for key in ("history", "turns", "transcript", "transcript_path", "session_config"):
        st.session_state.pop(key, None)
    st.rerun()


def load_artifacts(version_label: str) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], Any]:
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    declarations = load_tool_declarations(TOOLS_PATH)
    openai_tools = to_openai_tools(declarations)
    artifact_version = build_artifact_version(version_label, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    return system_prompt, declarations, openai_tools, artifact_version


def build_session_config(
    *,
    provider_name: str,
    model_name: str | None,
    selected_model: str,
    version_label: str,
    history_window: int,
    max_tool_rounds: int,
    artifact_version: Any,
) -> dict[str, Any]:
    return {
        "provider": provider_name,
        "model_override": model_name,
        "selected_model": selected_model,
        "version": version_label,
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "artifact_version": artifact_version.artifact_version,
        "prompt_hash": artifact_version.prompt_hash,
        "tools_hash": artifact_version.tools_hash,
    }


def start_transcript(config: dict[str, Any], artifact_version: Any) -> tuple[dict[str, Any], Path]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(
        [
            safe_slug(config["version"]),
            safe_slug(config["provider"]),
            timestamp,
        ]
    )
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": config["provider"],
        "model": config["selected_model"],
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": config["history_window"],
        "max_tool_rounds": config["max_tool_rounds"],
        "source": "streamlit_ui",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, transcript_path


def render_assistant_text(value: str) -> None:
    text = value or "_(Không có nội dung trả lời)_"
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        st.markdown(text)
    else:
        reply = parsed.get("reply") if isinstance(parsed, dict) else None
        if isinstance(reply, str) and reply.strip():
            st.markdown(reply)
        else:
            st.json(parsed)


def render_raw_response(value: str | None) -> None:
    text = value or ""
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        st.code(text or "No assistant response", language="text")
    else:
        st.json(parsed)


def render_tool_trace(turn: dict[str, Any]) -> None:
    status = turn.get("status", "unknown")
    rounds = turn.get("rounds", [])
    events = turn.get("tool_events", [])
    status_class = {
        "answered": "status-ok",
        "waiting_for_user": "status-wait",
        "provider_error": "status-error",
        "max_tool_rounds": "status-error",
    }.get(status, "status-neutral")
    st.markdown(
        (
            '<div class="trace-meta">'
            f'<span class="status-badge {status_class}">{escape(str(status))}</span>'
            f"<span>{len(rounds)} round(s)</span>"
            f"<span>•</span><span>{len(events)} tool call(s)</span>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    if turn.get("error"):
        st.error(turn["error"])

    if not rounds:
        return

    with st.expander("Tool trace", expanded=bool(events) or status != "answered"):
        for round_record in rounds:
            round_number = round_record.get("round", "?")
            st.markdown(f"**Round {round_number}**")

            assistant_text = round_record.get("assistant_text")
            if assistant_text:
                st.caption("Intermediate assistant text")
                st.code(assistant_text, language="text")

            calls = round_record.get("tool_calls", [])
            results = round_record.get("tool_results", [])
            if not calls:
                st.caption("No tool call in this round.")
                continue

            for index, call in enumerate(calls, start=1):
                tool_name = call.get("name", "unknown_tool")
                st.markdown(f"**{index}. `{tool_name}`**")
                st.caption("Arguments")
                st.json(call.get("args", {}))

                matching_result = results[index - 1] if index <= len(results) else None
                if matching_result is not None:
                    result = matching_result.get("result", matching_result)
                    if isinstance(result, dict) and result.get("error"):
                        st.error(f"Tool error: {result.get('error')}")
                    st.caption("Result")
                    st.json(result)


def render_chat_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn.get("user", ""))

    with st.chat_message("assistant"):
        if turn.get("status") == "provider_error":
            st.error("Provider không xử lý được yêu cầu này.")
        else:
            render_assistant_text(turn.get("assistant_text", ""))


def render_evidence_turn(turn: dict[str, Any]) -> None:
    turn_index = turn.get("turn_index", "?")
    st.markdown(f"#### Lượt {turn_index}")
    st.caption(f"User request: {turn.get('user', '')}")
    render_tool_trace(turn)
    with st.expander("Raw model response"):
        render_raw_response(turn.get("assistant_text"))


st.set_page_config(page_title="Northstar IT Helpdesk", page_icon="🛠️", layout="wide")
inject_styles()
initialize_session()
load_lab_env(ROOT)

st.markdown(
    """
    <section class="helpdesk-hero">
        <div class="hero-eyebrow">Northstar Labs · IT Helpdesk</div>
        <h1>Trợ lý IT, rõ từng bước xử lý.</h1>
        <p>
            Trao đổi với agent trong tab Chat. Khi cần kiểm tra kỹ thuật,
            mở tab Evidence &amp; Debug để xem tool, dữ liệu và transcript.
        </p>
        <div class="hero-pills">
            <span class="hero-pill">💬 Hội thoại nhiều lượt</span>
            <span class="hero-pill">🔎 Kiểm tra tool</span>
            <span class="hero-pill">↓ Lưu transcript</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

conversation_locked = bool(st.session_state.turns)

with st.sidebar:
    st.markdown("### 🧭 Phiên làm việc")
    st.caption("Chat ở màn hình chính; thông tin kỹ thuật nằm trong tab Evidence & Debug.")

    if st.button("＋ Cuộc hội thoại mới", use_container_width=True):
        reset_conversation()

    with st.expander("⚙️ Cấu hình nâng cao", expanded=False):
        provider_name = st.selectbox(
            "Provider",
            PROVIDERS,
            index=0,
            disabled=conversation_locked,
            help="Tạo cuộc hội thoại mới để đổi provider.",
        )
        version_label = st.text_input(
            "Artifact version",
            value="v0",
            disabled=conversation_locked,
            help="Nhãn phiên bản của prompt và tools, ví dụ v0 hoặc v3.",
        ).strip() or "v0"
        model_input = st.text_input(
            "Model override (không bắt buộc)",
            value="",
            disabled=conversation_locked,
            help="Để trống để dùng model mặc định của provider.",
        ).strip()
        history_window = st.number_input(
            "Số lượt ghi nhớ",
            min_value=1,
            max_value=20,
            value=5,
            step=1,
            disabled=conversation_locked,
        )
        max_tool_rounds = st.number_input(
            "Số vòng tool tối đa",
            min_value=1,
            max_value=10,
            value=4,
            step=1,
            disabled=conversation_locked,
        )

    if conversation_locked:
        st.caption("🔒 Cấu hình đã khóa cho transcript hiện tại.")

try:
    system_prompt, declarations, openai_tools, current_artifact_version = load_artifacts(version_label)
except Exception as exc:
    st.error(f"Không thể đọc artifacts: {type(exc).__name__}: {exc}")
    st.stop()

try:
    provider_preview = make_provider(provider_name)
    selected_model = model_input or getattr(provider_preview, "default_model", "provider-default")
except Exception as exc:
    st.error(f"Không thể khởi tạo provider: {type(exc).__name__}: {exc}")
    st.stop()

api_key_name = PROVIDER_API_KEYS[provider_name]
api_key_ready = bool(os.getenv(api_key_name))
session_config = st.session_state.session_config
artifact_changed = bool(
    session_config
    and session_config.get("artifact_version") != current_artifact_version.artifact_version
)

with st.sidebar:
    st.divider()
    if api_key_ready:
        st.success("Agent sẵn sàng")
    else:
        st.error(f"Thiếu {api_key_name} trong file .env")
    st.caption(f"{provider_name} · {selected_model} · {version_label}")

chat_tab, evidence_tab = st.tabs(["💬 Chat", "🔎 Evidence & Debug"])

suggested_prompt: str | None = None
typed_text: str | None = None

with chat_tab:
    st.caption("Hỏi agent về sự cố IT. Phần kỹ thuật được tách riêng để màn hình chat dễ đọc.")

    if artifact_changed:
        st.warning(
            "Prompt hoặc tools đã thay đổi trong lúc phiên chat đang mở. "
            "Hãy chọn **Cuộc hội thoại mới** để dùng đúng artifact hash."
        )

    if not st.session_state.turns:
        st.markdown(
            """
            <div class="empty-state">
                <h3>Bạn cần hỗ trợ vấn đề gì?</h3>
                <p>Chọn một câu hỏi mẫu hoặc nhập tình huống của riêng bạn.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        quick_columns = st.columns(len(QUICK_PROMPTS))
        for column, (label, prompt) in zip(quick_columns, QUICK_PROMPTS):
            if column.button(label, use_container_width=True, help=prompt):
                suggested_prompt = prompt

    for existing_turn in st.session_state.turns:
        render_chat_turn(existing_turn)

    with st.container():
        typed_text = st.chat_input(
            "Ví dụ: Kiểm tra trạng thái VPN production",
            disabled=artifact_changed,
        )

with evidence_tab:
    st.markdown("### Bằng chứng kỹ thuật")
    st.caption(
        "Dùng phần này khi demo hoặc kiểm tra agent: phiên bản artifact, "
        "tool calls, arguments, results/errors và transcript đều nằm tại đây."
    )

    st.markdown(
        (
            '<div class="session-strip">'
            '<div class="session-card"><span>Provider</span>'
            f'<strong>{escape(provider_name)}</strong></div>'
            '<div class="session-card"><span>Model</span>'
            f'<strong title="{escape(selected_model)}">{escape(selected_model)}</strong></div>'
            '<div class="session-card"><span>Artifact</span>'
            f'<strong title="{escape(current_artifact_version.artifact_version)}">'
            f'{escape(current_artifact_version.artifact_version)}</strong></div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    artifact_column, environment_column = st.columns(2)
    with artifact_column:
        st.markdown("**Artifact identity**")
        st.code(current_artifact_version.artifact_version, language="text")
        with st.expander("Full hashes"):
            st.caption("System prompt SHA-256")
            st.code(current_artifact_version.prompt_hash, language="text")
            st.caption("Tools SHA-256")
            st.code(current_artifact_version.tools_hash, language="text")

    with environment_column:
        st.markdown("**Runtime status**")
        st.write(f"Declared tools: `{len(declarations)}`")
        st.write(f"Provider key: `{'configured' if api_key_ready else 'missing'}`")
        st.write(f"Tavily key: `{'configured' if os.getenv('TAVILY_API_KEY') else 'not configured'}`")

    if st.session_state.transcript_path:
        st.markdown("**Transcript**")
        st.code(str(st.session_state.transcript_path), language="text")
        transcript_json = json.dumps(
            st.session_state.transcript,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
        st.download_button(
            "↓ Tải transcript JSON",
            data=transcript_json,
            file_name=st.session_state.transcript_path.name,
            mime="application/json",
        )
    else:
        st.info("Chưa có transcript. Hãy gửi ít nhất một câu hỏi trong tab Chat.")

    if st.session_state.turns:
        st.divider()
        st.markdown("### Trace theo từng lượt")
        for existing_turn in st.session_state.turns:
            render_evidence_turn(existing_turn)
            st.divider()

user_text = typed_text or suggested_prompt

if user_text:
    model_override = model_input or None

    if st.session_state.session_config is None:
        st.session_state.session_config = build_session_config(
            provider_name=provider_name,
            model_name=model_override,
            selected_model=selected_model,
            version_label=version_label,
            history_window=int(history_window),
            max_tool_rounds=int(max_tool_rounds),
            artifact_version=current_artifact_version,
        )
        transcript, transcript_path = start_transcript(
            st.session_state.session_config,
            current_artifact_version,
        )
        st.session_state.transcript = transcript
        st.session_state.transcript_path = transcript_path

    active_config = st.session_state.session_config
    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, active_config["history_window"]),
        {"role": "user", "content": user_text},
    ]

    try:
        provider = make_provider(active_config["provider"])
        with chat_tab:
            with st.spinner("Agent đang xử lý và gọi tool..."):
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=active_config["model_override"],
                    max_tool_rounds=active_config["max_tool_rounds"],
                )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
        st.session_state.history.extend(
            [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": assistant_text},
            ]
        )
    except Exception as exc:
        turn_record.update(
            {
                "status": "provider_error",
                "error": f"{type(exc).__name__}: {exc}",
            }
        )

    turn_record["ended_at"] = now_iso()
    st.session_state.turns.append(turn_record)
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
    st.rerun()
