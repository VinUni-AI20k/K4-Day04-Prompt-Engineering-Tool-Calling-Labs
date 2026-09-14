"""Streamlit UI for the IT Helpdesk Agent.

Reuses `run_model_tool_loop` from chat.py so the UI, CLI chat and eval evidence
share one agent loop. Run from starter_v0/:  streamlit run app.py
"""

from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import ARTIFACTS_DIR, ROOT, now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from tools.create_ticket.tool import TICKET_DIR
from versioning import artifact_version_dict, build_artifact_version


VERSIONS_DIR = ARTIFACTS_DIR / "versions"
TRANSCRIPTS_DIR = ROOT.parent / "evidence" / "transcripts"
PROVIDERS = ["openrouter", "openai", "anthropic", "gemini"]
ARTIFACT_SETS: dict[str, tuple[str, Path, Path]] = {
    "v5 · final (confirmation + safety)": ("v5", ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml"),
    "v4 · policy_area mapping": ("v4", VERSIONS_DIR / "v4" / "system_prompt.md", VERSIONS_DIR / "v4" / "tools.yaml"),
    "v3 · specific args": ("v3", VERSIONS_DIR / "v3" / "system_prompt.md", VERSIONS_DIR / "v3" / "tools.yaml"),
    "v2 · multi-turn + confirmation":("v2", VERSIONS_DIR / "v2" / "system_prompt.md", VERSIONS_DIR / "v1" / "tools.yaml"),
    "v1 · tool descriptions": ("v1", VERSIONS_DIR / "v1" / "system_prompt.md", VERSIONS_DIR / "v1" / "tools.yaml"),
    "v0 · starter baseline": ("v0", VERSIONS_DIR / "v0" / "system_prompt.md", VERSIONS_DIR / "v0" / "tools.yaml"),
}
SCENARIOS = [
    ("Bình thường", "Service status", "Kiểm tra trạng thái VPN production giúp mình."),
    ("Thiếu thông tin", "Không tự đoán ID", "Kiểm tra Wi-Fi trên laptop của mình."),
    ("Multi-tool", "Service + thiết bị", "VPN production có sự cố không? Kiểm tra luôn VPN trên máy LT-318."),
    ("Action boundary", "Xác nhận trước khi ghi", "Tạo ticket lỗi VPN cho máy LT-318 mức high."),
]
STATUS_LABELS = {
    "answered": ("Đã trả lời", "ok"),
    "waiting_for_user": ("Chờ người dùng", "wait"),
    "max_tool_rounds": ("Chạm giới hạn round", "warn"),
    "provider_error": ("Lỗi provider", "err"),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --pink-50: #FFF8FB; --pink-100: #FCE7F1; --pink-200: #F9D3E4; --pink-300: #F4B4D0;
  --pink-500: #D9468A; --pink-600: #B8336F; --ink: #3B2231; --muted: #8A6A7C;
  --line: #F2D5E3; --card: #FFFFFF;
  --ok-bg: #E7F6EE; --ok-fg: #1F7A4D; --warn-bg: #FFF3DC; --warn-fg: #9A6400;
  --err-bg: #FFE4E8; --err-fg: #B4233F; --wait-bg: #EFE7FF; --wait-fg: #6B45B8;
}
html, body, .stApp, .stMarkdown, .stButton button, .stTextInput input, .stSelectbox, label, p, h1, h2, h3, h4 {
  font-family: 'Be Vietnam Pro', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
.block-container { padding-top: 2rem; max-width: 1080px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #FDEAF3 0%, #FFF4F8 100%); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] h3 { font-size: .8rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 1.1rem 0 .3rem; }

.hero {
  background: radial-gradient(120% 140% at 0% 0%, #FFE1EE 0%, #FCEAF4 45%, #F6EEFF 100%);
  border: 1px solid var(--line); border-radius: 22px; padding: 1.6rem 1.8rem; margin-bottom: 1.2rem;
  box-shadow: 0 10px 30px -18px rgba(217, 70, 138, .45);
}
.hero-eyebrow { font-size: .75rem; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--pink-600); }
.hero h1 { font-size: 1.9rem; font-weight: 700; color: var(--ink); margin: .25rem 0 .35rem; line-height: 1.2; }
.hero p { color: var(--muted); margin: 0 0 .9rem; max-width: 46rem; }
.chips { display: flex; flex-wrap: wrap; gap: .4rem; }
.chip {
  display: inline-flex; align-items: center; gap: .35rem; background: rgba(255,255,255,.75);
  border: 1px solid var(--line); border-radius: 999px; padding: .18rem .65rem; font-size: .78rem; color: var(--ink);
  max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.chip b { font-weight: 600; color: var(--pink-600); }
.mono { font-family: 'JetBrains Mono', ui-monospace, Consolas, monospace; font-size: .76rem; }

.pill { display: inline-block; border-radius: 999px; padding: .1rem .6rem; font-size: .72rem; font-weight: 600; }
.pill.ok { background: var(--ok-bg); color: var(--ok-fg); }
.pill.warn { background: var(--warn-bg); color: var(--warn-fg); }
.pill.err { background: var(--err-bg); color: var(--err-fg); }
.pill.wait { background: var(--wait-bg); color: var(--wait-fg); }
.pill.soft { background: var(--pink-100); color: var(--pink-600); }
.meta-row { display: flex; flex-wrap: wrap; gap: .35rem; margin-bottom: .45rem; }

[data-testid="stChatMessage"] {
  background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: .9rem 1rem;
  box-shadow: 0 6px 18px -14px rgba(59, 34, 49, .35);
}
[data-testid="stExpander"] details { border: 1px solid var(--line); border-radius: 14px; background: #FFFCFD; }

.tool-card { border: 1px solid var(--line); border-left: 4px solid var(--pink-300); border-radius: 12px; padding: .55rem .8rem; margin: .6rem 0 .35rem; background: var(--card); }
.tool-card.err { border-left-color: #E5486A; background: #FFF7F9; }
.tool-card.wait { border-left-color: #9B7BE0; }
.tool-card.warn { border-left-color: #E9A23B; }
.tool-head { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem; }
.tool-name { font-family: 'JetBrains Mono', ui-monospace, Consolas, monospace; font-weight: 500; color: var(--ink); }
.round-label { font-size: .72rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin-top: .5rem; }
.sub-label { font-size: .72rem; color: var(--muted); margin: .2rem 0 .1rem; }

.scenario { border: 1px solid var(--line); border-radius: 16px; background: var(--card); padding: .8rem .9rem .2rem; height: 100%; }
.scenario .t { font-weight: 600; color: var(--ink); }
.scenario .d { font-size: .8rem; color: var(--muted); margin-bottom: .4rem; }

.stButton button { border-radius: 999px; border: 1px solid var(--pink-300); background: #FFFFFF; color: var(--pink-600); font-weight: 500; }
.stButton button:hover { border-color: var(--pink-500); color: #FFFFFF; background: var(--pink-500); }
.stat { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: .5rem .7rem; text-align: center; }
.stat .v { font-size: 1.25rem; font-weight: 700; color: var(--pink-600); line-height: 1.2; }
.stat .l { font-size: .7rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }
.footnote { font-size: .75rem; color: var(--muted); text-align: center; margin-top: 1.5rem; }
</style>
"""


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def parse_reply(text: str | None) -> dict[str, Any]:
    """The system prompt asks for JSON {intent, action, reply, evidence_ids}; fall back to raw text."""
    raw = (text or "").strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", raw, re.DOTALL)
    candidate = fenced.group(1) if fenced else raw
    try:
        data = json.loads(candidate)
    except (json.JSONDecodeError, TypeError):
        return {"reply": raw}
    if isinstance(data, dict) and "reply" in data:
        return data
    return {"reply": raw}


def event_state(result: Any) -> tuple[str, str]:
    if not isinstance(result, dict):
        return "Kết quả", "soft"
    if result.get("error"):
        return f"error · {result['error']}", "err"
    if result.get("awaiting_user"):
        return "awaiting_user", "wait"
    if result.get("status") == "needs_confirmation":
        return "needs_confirmation", "warn"
    if result.get("status"):
        return str(result["status"]), "ok"
    return "ok", "ok"


def ticket_count() -> int:
    return len(list(TICKET_DIR.glob("*.json"))) if TICKET_DIR.exists() else 0


def sidebar_config() -> dict[str, Any]:
    with st.sidebar:
        st.markdown("### Model provider")
        provider_name = st.selectbox("Provider", PROVIDERS, index=0)
        provider = make_provider(provider_name)
        default_model = getattr(provider, "default_model", "") or ""
        model = st.text_input("Model", value=default_model, help="Để trống để dùng model mặc định của provider.")
        key_env = getattr(provider, "api_key_env", None)
        if key_env:
            ready = bool(os.getenv(key_env))
            label, tone = ("API key đã cấu hình", "ok") if ready else (f"Thiếu {key_env} trong .env", "err")
            st.markdown(f'<span class="pill {tone}">{esc(label)}</span>', unsafe_allow_html=True)

        st.markdown("### Artifact")
        set_label = st.selectbox("Phiên bản prompt + tools", list(ARTIFACT_SETS), index=0)
        version, prompt_path, tools_path = ARTIFACT_SETS[set_label]
        artifact = build_artifact_version(version, prompt_path, tools_path)
        st.markdown(
            f'<div class="chips"><span class="chip mono">{esc(artifact.artifact_version)}</span></div>'
            f'<div class="sub-label">prompt_hash <span class="mono">{esc(artifact.prompt_hash[:16])}…</span><br>'
            f'tools_hash <span class="mono">{esc(artifact.tools_hash[:16])}…</span></div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Hội thoại")
        history_window = st.slider("History window (cặp lượt)", 0, 10, 5)
        max_rounds = st.slider("Max tool rounds", 1, 6, 4)
        if st.button("＋ Cuộc hội thoại mới", use_container_width=True):
            st.session_state.pop("config_key", None)

    declarations = load_tool_declarations(tools_path)
    return {
        "provider": provider_name,
        "model": model.strip() or None,
        "version": version,
        "prompt_path": prompt_path,
        "tools_path": tools_path,
        "system_prompt": prompt_path.read_text(encoding="utf-8"),
        "tool_names": [item["name"] for item in declarations],
        "openai_tools": to_openai_tools(declarations),
        "artifact": artifact,
        "history_window": history_window,
        "max_rounds": max_rounds,
        "key": (provider_name, model.strip(), artifact.artifact_version),
    }


def ensure_session(cfg: dict[str, Any]) -> None:
    if st.session_state.get("config_key") == cfg["key"]:
        return
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(cfg["version"]), safe_slug(cfg["provider"]), "ui", timestamp])
    st.session_state.config_key = cfg["key"]
    st.session_state.history = []
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        "client": "streamlit_ui",
        **artifact_version_dict(cfg["artifact"]),
        "provider": cfg["provider"],
        "model": cfg["model"],
        "system_prompt": str(cfg["prompt_path"]),
        "tools": str(cfg["tools_path"]),
        "history_window": cfg["history_window"],
        "max_tool_rounds": cfg["max_rounds"],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def run_turn(user_text: str, cfg: dict[str, Any]) -> None:
    transcript = st.session_state.transcript
    history: list[dict[str, str]] = st.session_state.history
    messages = [
        {"role": "system", "content": cfg["system_prompt"]},
        *trim_history(history, cfg["history_window"]),
        {"role": "user", "content": user_text},
    ]
    turn: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    try:
        result = run_model_tool_loop(
            provider=make_provider(cfg["provider"]),
            messages=messages,
            tools=cfg["openai_tools"],
            model=cfg["model"],
            max_tool_rounds=cfg["max_rounds"],
        )
        turn.update(result)
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": result["assistant_text"]})
    except Exception as exc:  # surface provider failures in the UI and transcript
        turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
    turn["ended_at"] = now_iso()
    transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, transcript)


def render_hero(cfg: dict[str, Any]) -> None:
    turns = st.session_state.transcript["turns"]
    calls = sum(len(turn.get("tool_events", [])) for turn in turns)
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-eyebrow">Northstar Labs · IT Service Desk</div>
          <h1>Helpdesk Agent Console</h1>
          <p>Trợ lý kiểm tra service, thiết bị, tài khoản, knowledge base và chính sách IT.
             Mọi tool call, argument và kết quả đều hiển thị để audit.</p>
          <div class="chips">
            <span class="chip"><b>artifact</b><span class="mono">{esc(cfg['artifact'].artifact_version)}</span></span>
            <span class="chip"><b>provider</b>{esc(cfg['provider'])}</span>
            <span class="chip"><b>model</b>{esc(cfg['model'] or 'mặc định')}</span>
            <span class="chip"><b>tools</b>{len(cfg['tool_names'])}</span>
            <span class="chip"><b>lượt</b>{len(turns)}</span>
            <span class="chip"><b>tool calls</b>{calls}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tool_event(event: dict[str, Any]) -> None:
    result = event.get("result")
    label, tone = event_state(result)
    st.markdown(
        f'<div class="tool-card {tone}"><div class="tool-head">'
        f'<span class="tool-name">{esc(event.get("tool"))}</span>'
        f'<span class="pill {tone}">{esc(label)}</span></div></div>',
        unsafe_allow_html=True,
    )
    args_col, result_col = st.columns([2, 3])
    with args_col:
        st.markdown('<div class="sub-label">Arguments</div>', unsafe_allow_html=True)
        st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
    with result_col:
        st.markdown('<div class="sub-label">Result / error</div>', unsafe_allow_html=True)
        st.code(json.dumps(result, ensure_ascii=False, indent=2, default=str), language="json")


def render_turn(turn: dict[str, Any], is_last: bool) -> None:
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(turn["user"])

    with st.chat_message("assistant", avatar="🌸"):
        status_label, status_tone = STATUS_LABELS.get(turn.get("status", ""), (turn.get("status", ""), "soft"))
        if turn.get("status") == "provider_error":
            st.markdown(f'<span class="pill err">{esc(status_label)}</span>', unsafe_allow_html=True)
            st.error(turn.get("error", "Provider error"))
            return

        parsed = parse_reply(turn.get("assistant_text"))
        chips = [f'<span class="pill {status_tone}">{esc(status_label)}</span>']
        for field in ("intent", "action"):
            if parsed.get(field):
                chips.append(f'<span class="pill soft">{field}: {esc(parsed[field])}</span>')
        for evidence_id in parsed.get("evidence_ids") or []:
            chips.append(f'<span class="pill soft mono">{esc(evidence_id)}</span>')
        st.markdown(f'<div class="meta-row">{"".join(chips)}</div>', unsafe_allow_html=True)
        st.markdown(str(parsed.get("reply") or ""))

        events = turn.get("tool_events", [])
        for event in events:
            result = event.get("result")
            if event.get("tool") == "format_incident_report" and isinstance(result, dict) and result.get("markdown"):
                with st.container(border=True):
                    st.markdown(result["markdown"])

        last_result = events[-1].get("result") if events else None
        if is_last and turn.get("status") == "waiting_for_user" and isinstance(last_result, dict):
            options: list[str] = []
            if last_result.get("response_type") == "yes_no":
                options = ["Có, tôi xác nhận", "Không, huỷ yêu cầu"]
            elif last_result.get("response_type") == "choice":
                options = [str(option) for option in last_result.get("options") or []]
            if options:
                cols = st.columns(min(len(options), 4))
                for index, option in enumerate(options):
                    if cols[index % len(cols)].button(option, key=f"quick_{turn['turn_index']}_{index}"):
                        st.session_state.queued = option

        rounds = turn.get("rounds", [])
        title = f"Tool trace · {len(events)} call · {len(rounds)} round"
        with st.expander(title, expanded=is_last and bool(events)):
            if not events:
                st.caption("Không có tool call — agent trả lời trực tiếp.")
            for round_record in rounds:
                st.markdown(f'<div class="round-label">Round {round_record["round"]}</div>', unsafe_allow_html=True)
                if not round_record.get("tool_results"):
                    st.caption("Model trả lời, không gọi tool.")
                for event in round_record.get("tool_results", []):
                    render_tool_event(event)


def render_empty_state() -> None:
    st.markdown("#### Bắt đầu với một kịch bản")
    cols = st.columns(len(SCENARIOS))
    for col, (title, desc, prompt) in zip(cols, SCENARIOS):
        with col:
            st.markdown(f'<div class="scenario"><div class="t">{esc(title)}</div><div class="d">{esc(desc)}</div></div>', unsafe_allow_html=True)
            if st.button("Thử ngay", key=f"scenario_{title}", use_container_width=True, help=prompt):
                st.session_state.queued = prompt


def render_sidebar_stats() -> None:
    turns = st.session_state.transcript["turns"]
    calls = sum(len(turn.get("tool_events", [])) for turn in turns)
    errors = sum(
        1 for turn in turns for event in turn.get("tool_events", [])
        if isinstance(event.get("result"), dict) and event["result"].get("error")
    )
    with st.sidebar:
        st.markdown("### Phiên hiện tại")
        stats = [(len(turns), "lượt"), (calls, "tool calls"), (errors, "tool errors"), (ticket_count(), "tickets local")]
        cols = st.columns(2)
        for index, (value, label) in enumerate(stats):
            cols[index % 2].markdown(f'<div class="stat"><div class="v">{value}</div><div class="l">{esc(label)}</div></div>', unsafe_allow_html=True)
        path: Path = st.session_state.transcript_path
        saved = path.exists()
        st.markdown(
            f'<div class="sub-label" style="margin-top:.6rem">Transcript {"đã lưu" if saved else "sẽ lưu sau lượt đầu"}</div>'
            f'<div class="mono" style="word-break:break-all">{esc(path.relative_to(ROOT.parent))}</div>',
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(page_title="Helpdesk Agent Console", page_icon="🌸", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    cfg = sidebar_config()
    ensure_session(cfg)
    render_hero(cfg)

    turns = st.session_state.transcript["turns"]
    if not turns:
        render_empty_state()
    for index, turn in enumerate(turns):
        render_turn(turn, is_last=index == len(turns) - 1)

    prompt = st.chat_input("Mô tả sự cố IT, ví dụ: Kiểm tra VPN trên máy LT-204…")
    queued = st.session_state.pop("queued", None)
    prompt = prompt or queued
    if prompt:
        with st.spinner("Agent đang xử lý và gọi tool…"):
            run_turn(prompt, cfg)
        st.rerun()

    render_sidebar_stats()
    st.markdown('<div class="footnote">Dữ liệu employee, asset, incident và policy đều là dữ liệu giả lập cho bài lab.</div>', unsafe_allow_html=True)


main()
