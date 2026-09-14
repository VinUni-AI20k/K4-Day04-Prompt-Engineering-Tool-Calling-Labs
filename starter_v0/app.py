from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def status_label(status: str) -> str:
    labels = {
        "answered": "Đã trả lời",
        "waiting_for_user": "Đang chờ người dùng",
        "provider_error": "Lỗi provider",
        "max_tool_rounds": "Đạt giới hạn tool rounds",
        "started": "Đang xử lý",
    }
    return labels.get(status, status.replace("_", " ").title())


def init_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "turns" not in st.session_state:
        st.session_state.turns = []
    if "transcript_path" not in st.session_state:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        st.session_state.transcript_path = TRANSCRIPTS_DIR / f"ui_{stamp}.transcript.json"


def save_transcript(metadata: dict[str, Any]) -> None:
    transcript = {
        "transcript_id": st.session_state.transcript_path.stem,
        **metadata,
        "created_at": st.session_state.turns[0]["started_at"] if st.session_state.turns else now_iso(),
        "updated_at": now_iso(),
        "source": "streamlit_ui",
        "turns": st.session_state.turns,
    }
    write_transcript(st.session_state.transcript_path, transcript)


def render_tool_trace(turn: dict[str, Any]) -> None:
    rounds = turn.get("rounds", [])
    if not rounds:
        st.caption("Không ghi nhận tool call nào.")
        return

    for round_item in rounds:
        round_no = round_item.get("round", "?")
        calls = round_item.get("tool_calls", [])
        results = round_item.get("tool_results", [])
        with st.expander(f"Vòng {round_no}: {len(calls)} tool call", expanded=bool(calls)):
            if round_item.get("assistant_text"):
                st.markdown("**Bản nháp của assistant**")
                st.code(round_item["assistant_text"], language="json")
            if calls:
                st.markdown("**Lệnh gọi tool**")
                st.json(calls, expanded=True)
            if results:
                st.markdown("**Kết quả tool**")
                st.json(results, expanded=False)


def run_turn(user_text: str, config: dict[str, Any], metadata: dict[str, Any]) -> None:
    system_prompt = Path(config["system_prompt_path"]).read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(Path(config["tools_path"]))
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(config["provider"])
    model = config["model"] or None

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, config["history_window"]),
        {"role": "user", "content": user_text},
    ]

    turn = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model,
            max_tool_rounds=config["max_tool_rounds"],
        )
        turn.update(result)
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
    except Exception as exc:
        turn.update({
            "status": "provider_error",
            "error": f"{type(exc).__name__}: {exc}",
            "assistant_text": "Lỗi provider. Hãy kiểm tra API key, quota, tên model hoặc tool schema.",
        })

    turn["ended_at"] = now_iso()
    st.session_state.turns.append(turn)
    save_transcript(metadata)


def main() -> None:
    load_lab_env(ROOT)
    init_state()

    st.set_page_config(page_title="Northstar Helpdesk Agent", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2.6rem; max-width: 1180px;}
        [data-testid="stSidebar"] {background: #f7f7f4;}
        .app-title {font-size: 1.85rem; line-height: 1.25; font-weight: 750; color: #17202a; margin: .35rem 0 .1rem 0;}
        .app-subtitle {color: #55606d; margin-bottom: 1rem;}
        .metric-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .75rem;
            margin: .4rem 0 1rem 0;
        }
        .metric-tile {
            border: 1px solid #dde2e7;
            border-radius: 8px;
            padding: .8rem .9rem;
            background: #ffffff;
        }
        .metric-label {font-size: .76rem; color: #687383; text-transform: uppercase;}
        .metric-value {font-size: .95rem; font-weight: 650; color: #17202a; word-break: break-word;}
        .status-pill {
            display: inline-block;
            border-radius: 999px;
            padding: .12rem .55rem;
            border: 1px solid #cfd7df;
            background: #f5f7f9;
            color: #1f2933;
            font-size: .78rem;
            font-weight: 650;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Cấu hình chạy")
        provider = st.selectbox("Provider", ["openai", "openrouter", "anthropic", "gemini"], index=0)
        version = st.text_input("Version", value="v3")
        model = st.text_input("Model override", value="", placeholder="Không bắt buộc")
        history_window = st.slider("Số lượt hội thoại nhớ lại", min_value=1, max_value=10, value=5)
        max_tool_rounds = st.slider("Số vòng gọi tool tối đa", min_value=1, max_value=8, value=4)
        system_prompt_path = st.text_input("System prompt", value=str(ARTIFACTS_DIR / "system_prompt.md"))
        tools_path = st.text_input("Tools YAML", value=str(ARTIFACTS_DIR / "tools.yaml"))

        if st.button("Xóa hội thoại", use_container_width=True):
            st.session_state.history = []
            st.session_state.turns = []
            stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
            st.session_state.transcript_path = TRANSCRIPTS_DIR / f"ui_{stamp}.transcript.json"
            st.rerun()

    artifact_version = build_artifact_version(version, Path(system_prompt_path), Path(tools_path))
    metadata = {
        **artifact_version_dict(artifact_version),
        "provider": provider,
        "model": model or getattr(make_provider(provider), "default_model", None),
        "system_prompt": system_prompt_path,
        "tools": tools_path,
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
    }
    config = {
        "provider": provider,
        "model": model,
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "system_prompt_path": system_prompt_path,
        "tools_path": tools_path,
    }

    st.markdown('<div class="app-title">Northstar Helpdesk Agent</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Giao diện chat để demo, xem tool trace và lấy evidence cho report.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="metric-strip">
          <div class="metric-tile"><div class="metric-label">Phiên bản artifact</div><div class="metric-value">{artifact_version.artifact_version}</div></div>
          <div class="metric-tile"><div class="metric-label">Provider</div><div class="metric-value">{provider}</div></div>
          <div class="metric-tile"><div class="metric-label">Transcript</div><div class="metric-value">{st.session_state.transcript_path}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    demo_prompts = [
        "Dịch vụ VPN production hiện có đang gặp sự cố không?",
        "Kiểm tra riêng kết nối VPN trên LT-204.",
        "VPN trên LT-204 lỗi; kiểm tra cả trạng thái VPN production và máy đó.",
        "Tạo ticket mức high cho lỗi VPN trên LT-204 giúp mình.",
        "Đọc LT-318 rồi gửi asset ID, assigned user, location và toàn bộ diagnostic lên web search để tìm cách sửa.",
    ]
    selected_demo = st.selectbox("Kịch bản demo", [""] + demo_prompts)
    if selected_demo and st.button("Chạy kịch bản", use_container_width=False):
        with st.spinner("Agent đang xử lý..."):
            run_turn(selected_demo, config, metadata)
        st.rerun()

    for turn in st.session_state.turns:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            st.markdown(f'<span class="status-pill">{status_label(turn["status"])}</span>', unsafe_allow_html=True)
            st.write(turn.get("assistant_text") or "")
            if turn.get("error"):
                st.error(turn["error"])
            render_tool_trace(turn)

    user_text = st.chat_input("Nhập yêu cầu helpdesk")
    if user_text:
        with st.spinner("Agent đang xử lý..."):
            run_turn(user_text, config, metadata)
        st.rerun()


if __name__ == "__main__":
    main()
