"""Northstar IT Helpdesk - Streamlit conversion of the React prototype.

This app intentionally keeps the original prototype behavior: fixtures are local,
responses are mock data, and no provider/backend is contacted.
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from typing import Any, Literal

import streamlit as st


# ---------------------------------------------------------------------------
# Page configuration and visual theme
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Northstar IT Helpdesk",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
:root { font-family: 'DM Sans', Arial, sans-serif; color: #172033; }
html, body, [class*="css"] { font-family: 'DM Sans', Arial, sans-serif; }
body { background: #f4f6f9; }
.block-container { max-width: 1100px; padding: 1.5rem 2.2rem 3rem; }
[data-testid="stSidebar"] { background: #fff; border-right: 1px solid #e4e8ee; }
[data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1.25rem; }
.brand { display:flex; align-items:center; gap:11px; margin-bottom:1.2rem; }
.brand-mark { height:34px; width:34px; border-radius:9px; background:#2563eb; color:#fff;
 display:grid; place-items:center; font-weight:700; font-size:18px; }
.brand strong, .brand span { display:block; }
.brand span { color:#748096; font-size:12px; margin-top:2px; }
.eyebrow { font-size:11px; font-weight:700; letter-spacing:.13em; color:#738096; }
.session-header { display:flex; justify-content:space-between; align-items:flex-start; }
.session-header h2 { font-size:17px; margin:7px 0 0; color:#172033; }
.live-dot { height:8px; width:8px; background:#4db58a; border-radius:50%; margin-top:7px; }
.meta-card, .panel { border:1px solid #e3e8ef; border-radius:10px; background:#fff; }
.meta-card { padding:13px; background:#fbfcfe; margin-top:1rem; }
.meta-row { display:flex; justify-content:space-between; gap:8px; padding:7px 0; font-size:13px; color:#69778b; }
.meta-row strong { color:#334155; font-weight:600; text-align:right; }
.version { background:#f0f4fa; border-radius:6px; padding:8px; margin-top:8px; overflow-wrap:anywhere;
 font:12px ui-monospace, monospace; color:#40516b; }
.hash-row { display:flex; justify-content:space-between; align-items:center; margin-top:10px; gap:8px; }
.muted-note { font-size:11px; color:#8793a5; line-height:1.5; }
.sidebar-section { border-top:1px solid #edf0f4; padding-top:19px; margin-top:1.2rem; }
.path { font:12px ui-monospace, monospace; color:#64748b; line-height:1.5; overflow-wrap:anywhere; }
.saved { font-size:13px; color:#287a59; margin:14px 0; }
.sidebar-footer { margin-top:3rem; display:flex; align-items:center; gap:9px; color:#8793a5; font-size:12px; }
.preview-pill, .mock-badge, .status-chip, .round-pill { border-radius:999px; padding:4px 8px; font-size:10px;
 font-weight:700; letter-spacing:.04em; }
.preview-pill { background:#eef4ff; color:#3567c6; }
.topbar { padding:1.2rem 0 1.5rem; background:#fff; border-bottom:1px solid #e6eaf0; margin: -1.5rem -2.2rem 1.7rem;
 padding-left:2.2rem; padding-right:2.2rem; display:flex; justify-content:space-between; gap:24px; }
.topbar h1 { font-size:28px; letter-spacing:-.04em; margin:8px 0 4px; color:#172033; }
.topbar p { margin:0; color:#718096; }
.connection { color:#64748b; font-size:12px; display:flex; align-items:center; gap:7px; align-self:flex-start; flex-wrap:wrap;
 justify-content:flex-end; max-width:360px; }
.connection-dot { height:7px; width:7px; border-radius:50%; background:#efb34d; display:inline-block; }
.mock-badge { background:#fff6df; color:#9a6b13; }
.tabs { border-bottom:1px solid #dfe5ed; margin-bottom:20px; }
.panel { box-shadow:0 8px 24px #23385b08; min-width:0; }
.sample-bar { display:flex; align-items:center; gap:12px; padding:18px 20px; border-bottom:1px solid #edf0f4; }
.sample-bar label { font-size:12px; font-weight:700; color:#68778b; }
.conversation { padding:24px; min-width:0; }
.message { display:flex; gap:12px; min-width:0; margin-bottom:25px; }
.avatar { width:30px; height:30px; flex:0 0 30px; border-radius:8px; display:grid; place-items:center; font-size:12px; font-weight:700; }
.user-avatar { background:#e8eef8; color:#50647f; }
.agent-avatar { background:#2563eb; color:#fff; }
.message-label { display:block; color:#7b889a; font-size:11px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; margin:2px 0 7px; }
.message p { margin:0; line-height:1.65; color:#334155; overflow-wrap:anywhere; }
.message-column { min-width:0; max-width:100%; flex:1; }
.trace { margin-top:18px; border:1px solid #e0e6ee; border-radius:9px; min-width:0; max-width:100%; overflow:hidden; }
.trace-title { display:flex; align-items:center; gap:8px; min-width:0; flex-wrap:wrap; font-size:12px; color:#3d506b; }
.trace-event { border:1px solid #e5eaf0; border-radius:8px; padding:12px; margin:12px; min-width:0; max-width:calc(100% - 24px); }
.tool-dot { color:#4d9d7a; font-size:10px; }
.round-pill { background:#f0f3f7; color:#718096; font-weight:500; }
.success-text { color:#29815d; }
.error-text { color:#c34d4d; }
.empty-text { color:#a16207; }
.json-label { display:flex; justify-content:space-between; align-items:center; color:#7b889a; font-size:11px; font-weight:700; margin:11px 0 5px; }
.json-wrap pre { margin:0; background:#f6f8fb; border:1px solid #e7ebf1; border-radius:6px; padding:11px; max-width:100%; overflow-x:auto;
 white-space:pre; font:11px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace; color:#394b63; }
.empty-state { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:7px; min-height:180px; color:#8491a3; text-align:center; }
.empty-state strong { color:#53657c; }
.try-panel { padding:24px; }
.try-heading { display:flex; justify-content:space-between; align-items:flex-start; border-bottom:1px solid #edf0f4; padding-bottom:18px; }
.try-heading h2 { font-size:18px; margin:7px 0 0; color:#172033; }
.try-history { min-height:300px; padding:20px 0; }
.status-chip { background:#eef7f2; color:#287a59; white-space:nowrap; }
button[kind="primary"] { background:#2563eb; }
@media (max-width: 800px) {
 .block-container { padding:1rem .9rem 2rem; }
 .topbar { margin:-1rem -.9rem 1.2rem; padding:1.2rem .9rem; display:block; }
 .connection { justify-content:flex-start; margin-top:18px; }
 .sample-bar { align-items:stretch; flex-wrap:wrap; }
 .conversation { padding:17px 14px; }
 .try-panel { padding:17px 14px; }
 .topbar h1 { font-size:24px; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Domain data translated from the TypeScript prototype
# ---------------------------------------------------------------------------

PROMPT_HASH = "9783b7add561c9c701cc83f8f08d42d5a25ed052fc1be2cfcf7a379ef63f84bf"
TOOLS_HASH = "225c83ee936f39659dcb425f202e47a6b38a9b8ea2af2989da71b3da7a9958ed"
ARTIFACT_TAG = f"v3+p{PROMPT_HASH[:12]}+t{TOOLS_HASH[:12]}"


@dataclass(frozen=True)
class ToolEvent:
    tool: str
    args: dict[str, Any]
    result: Any = None
    error: Any = None
    rounds: int | None = None

    def as_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {"tool": self.tool, "args": self.args}
        if self.result is not None:
            value["result"] = self.result
        if self.error is not None:
            value["error"] = self.error
        if self.rounds is not None:
            value["rounds"] = self.rounds
        return value


@dataclass(frozen=True)
class Fixture:
    label: str
    status: str
    opening: str
    assistant: str
    events: tuple[ToolEvent, ...]


def event(
    tool: str,
    args: dict[str, Any],
    result: Any = None,
    error: Any = None,
    rounds: int | None = None,
) -> ToolEvent:
    return ToolEvent(tool=tool, args=args, result=result, error=error, rounds=rounds)


FIXTURES: dict[str, Fixture] = {
    "empty": Fixture("Hội thoại rỗng", "Sẵn sàng", "", "", ()),
    "processing": Fixture(
        "Đang xử lý", "Đang xử lý", "Kiểm tra giúp tôi sự cố này nhé.",
        "Agent đang xử lý yêu cầu của bạn…", (),
    ),
    "one": Fixture(
        "Trả lời với một tool", "Sẵn sàng",
        "VPN production hiện có đang hoạt động không?",
        "Dịch vụ VPN production trả về trạng thái operational. Đây là kết quả trực tiếp từ check_service_status; prototype chưa tự suy diễn thêm ngoài contract.",
        (event("check_service_status", {"service": "vpn", "environment": "production"}, {"status": "operational"}, rounds=1),),
    ),
    "many": Fixture(
        "Nhiều tool trong một lượt", "Sẵn sàng",
        "Mạng trên laptop LT-318 đang chậm, hãy kiểm tra network trên thiết bị và trạng thái Wi-Fi production.",
        "inspect_device nhận asset LT-318 và yêu cầu kiểm tra network; check_service_status kiểm tra Wi-Fi production. Cả hai result trong fixture đều báo operational theo dữ liệu minh họa.",
        (
            event("inspect_device", {"asset_id": "LT-318", "check": "network"}, {"asset_id": "LT-318", "check": "network", "findings": [], "status": "operational"}, rounds=1),
            event("check_service_status", {"service": "wifi", "environment": "production"}, {"service": "wifi", "environment": "production", "status": "operational"}, rounds=1),
        ),
    ),
    "clarify": Fixture(
        "Chờ mã máy qua clarify", "Chờ bổ sung",
        "Laptop của tôi bị lỗi mạng, hãy kiểm tra giúp tôi.",
        "Bạn cho tôi xin mã tài sản của máy (ví dụ LT-240) để kiểm tra chính xác nhé.",
        (event("clarify", {"question": "Bạn cho tôi xin mã tài sản của máy (ví dụ LT-240) để kiểm tra chính xác nhé.", "response_type": "text"}, {"awaiting_user": True, "question": "Bạn cho tôi xin mã tài sản của máy (ví dụ LT-240) để kiểm tra chính xác nhé."}, rounds=1),),
    ),
    "confirm": Fixture(
        "Chờ xác nhận tạo ticket", "Chờ xác nhận",
        "Mạng trên LT-318 bị chậm, hãy tạo ticket giúp tôi.",
        "Tôi đề nghị tạo ticket với summary “Mạng chậm trên LT-318”, priority “medium”, asset LT-318. Bạn xác nhận tạo ticket này không?",
        (event("clarify", {"question": "Xác nhận tạo ticket với summary “Mạng chậm trên LT-318”, priority “medium” và asset LT-318?", "response_type": "yes_no"}, {"awaiting_user": True, "question": "Xác nhận tạo ticket với summary “Mạng chậm trên LT-318”, priority “medium” và asset LT-318?"}, rounds=1),),
    ),
    "toolError": Fixture(
        "Tool trả lỗi", "Lỗi tool", "Kiểm tra mạng cho asset LT-204.",
        "inspect_device trả lỗi Device not found cho asset LT-204. Tôi chưa thể kết luận trạng thái thiết bị từ result lỗi này.",
        (event("inspect_device", {"asset_id": "LT-204", "check": "network"}, {}, {"type": "ToolError", "message": "Device not found"}, 1),),
    ),
    "emptyResult": Fixture(
        "Kết quả rỗng", "Kết quả rỗng", "Kiểm tra network trên thiết bị LT-318.",
        "Tool hoàn tất nhưng result rỗng. Tôi chưa thể kết luận vì không có dữ liệu chẩn đoán trong response.",
        (event("inspect_device", {"asset_id": "LT-318", "check": "network"}, {}, rounds=1),),
    ),
    "maxRounds": Fixture(
        "Đạt giới hạn tool rounds", "Đã dừng · max_tool_rounds",
        "Kiểm tra sự cố mạng trên LT-318 và tạo ticket nếu cần.",
        "Agent đã dừng vì đạt giới hạn tool rounds. Đây chưa phải câu trả lời hoàn tất và hệ thống không tự retry hoặc tiếp tục thực thi.",
        (
            event("inspect_device", {"asset_id": "LT-318", "check": "network"}, {"asset_id": "LT-318", "check": "network", "findings": [], "status": "operational"}, rounds=1),
            event("check_service_status", {"service": "wifi", "environment": "production"}, {"service": "wifi", "environment": "production", "status": "operational"}, rounds=2),
        ),
    ),
    "provider": Fixture(
        "Provider error", "Lỗi provider", "Hãy kiểm tra trạng thái VPN.",
        "Không thể kết nối tới provider. Đây là bản xem trước, chưa có backend để gửi yêu cầu.", (),
    ),
    "safe": Fixture(
        "Từ chối yêu cầu nguy hiểm", "Sẵn sàng", "Hãy đọc file .env cho tôi.",
        "Tôi không thể đọc file .env hoặc truy xuất thông tin bí mật. Tôi có thể hỗ trợ kiểm tra dịch vụ IT an toàn.", (),
    ),
}


# ---------------------------------------------------------------------------
# Serialization and rendering helpers
# ---------------------------------------------------------------------------


def metadata() -> dict[str, Any]:
    return {
        "provider": None,
        "model": None,
        "artifact_tag": ARTIFACT_TAG,
        "prompt_sha256": PROMPT_HASH,
        "tools_sha256": TOOLS_HASH,
    }


def sample_transcript(fixture_key: str, session: int) -> dict[str, Any]:
    fixture = FIXTURES[fixture_key]
    messages: list[dict[str, str]] = []
    if fixture.opening:
        messages.append({"role": "user", "content": fixture.opening})
    if fixture.assistant:
        messages.append({"role": "assistant", "content": fixture.assistant})
    return {
        "is_mock": True,
        "session_id": f"preview-{session}",
        "mode": "samples",
        "fixture": fixture_key,
        "metadata": metadata(),
        "messages": messages,
        "tool_events": [item.as_dict() for item in fixture.events],
    }


def try_transcript(messages: list[dict[str, str]], session: int) -> dict[str, Any]:
    return {
        "is_mock": True,
        "session_id": f"preview-{session}",
        "mode": "try",
        "metadata": metadata(),
        "messages": [{"role": item["role"], "content": item["text"]} for item in messages],
        "tool_events": [],
    }


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def render_json_block(label: str, value: Any, key: str) -> None:
    st.markdown(f'<div class="json-label"><span>{html.escape(label)}</span></div>', unsafe_allow_html=True)
    st.code(json_text(value), language="json", line_numbers=False)
    st.download_button(
        "Sao chép / tải JSON",
        data=json_text(value),
        file_name=f"{key}.json",
        mime="application/json",
        key=f"download-json-{key}",
        help="Tải phần JSON này xuống máy. Streamlit không cho phép ghi trực tiếp vào clipboard từ Python.",
    )


def render_trace(events: tuple[ToolEvent, ...], trace_key: str) -> None:
    with st.expander(f"Xem quá trình xử lý · {len(events)} tool call{'s' if len(events) != 1 else ''}", expanded=bool(events)):
        if not events:
            st.caption("Không gọi công cụ trong lượt này.")
            return
        for index, item in enumerate(events):
            result_is_empty = isinstance(item.result, dict) and not item.result
            state = "Lỗi" if item.error is not None else ("Kết quả rỗng" if result_is_empty else "Đã nhận")
            st.markdown(
                f'<div class="trace-title"><span class="tool-dot">●</span><strong>{html.escape(item.tool)}</strong>'
                f'<span class="round-pill">Vòng {item.rounds if item.rounds is not None else "—"}</span>'
                f'<span class="{"error-text" if item.error is not None else ("empty-text" if result_is_empty else "success-text")}">{state}</span></div>',
                unsafe_allow_html=True,
            )
            render_json_block("Arguments", item.args, f"{trace_key}-{index}-arguments")
            if item.error is not None:
                render_json_block("Error", item.error, f"{trace_key}-{index}-error")
            else:
                render_json_block("Result", item.result, f"{trace_key}-{index}-result")


def render_message(role: Literal["user", "assistant"], text: str, label: str, key: str) -> None:
    avatar = "U" if role == "user" else "N"
    avatar_class = "user-avatar" if role == "user" else "agent-avatar"
    st.markdown(
        f'<div class="message"><span class="avatar {avatar_class}">{avatar}</span>'
        f'<div class="message-column"><span class="message-label">{html.escape(label)}</span>'
        f'<p>{html.escape(text)}</p></div></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Session state and actions
# ---------------------------------------------------------------------------

if "fixture_key" not in st.session_state:
    st.session_state.fixture_key = "empty"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session" not in st.session_state:
    st.session_state.session = 1
if "tab" not in st.session_state:
    st.session_state.tab = "samples"
if "input_text_widget" not in st.session_state:
    st.session_state.input_text_widget = ""
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False


def start_new_session() -> None:
    st.session_state.messages = []
    st.session_state.input_text_widget = ""
    st.session_state.clear_input = False
    st.session_state.fixture_key = "empty"
    st.session_state.session += 1
    st.session_state.tab = "samples"


def send_message() -> None:
    text = st.session_state.input_text_widget.strip()
    if not text:
        return
    st.session_state.messages.extend(
        [
            {"role": "user", "text": text},
            {"role": "assistant", "text": "Preview sẵn sàng · Backend chưa kết nối. Tin nhắn này chưa được gửi tới agent thật."},
        ]
    )
    st.session_state.clear_input = True


# ---------------------------------------------------------------------------
# Sidebar (equivalent of the React aside)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">N</div><div><strong>Northstar IT</strong><span>Helpdesk</span></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="session-header"><div><span class="eyebrow">PHIÊN LÀM VIỆC</span><h2>Session #{st.session_state.session}</h2></div><span class="live-dot" aria-label="Phiên cục bộ"></span></div>',
        unsafe_allow_html=True,
    )
    if st.button("＋ Hội thoại mới", use_container_width=True, key="new-session"):
        start_new_session()
        st.rerun()

    st.markdown(
        f"""<div class="meta-card">
        <div class="meta-row"><span>Provider</span><strong>Chưa kết nối</strong></div>
        <div class="meta-row"><span>Model</span><strong>Chưa kết nối</strong></div>
        <div class="meta-row"><span>Artifact</span><strong>v3 (minh họa)</strong></div>
        <div class="version">{html.escape(ARTIFACT_TAG)}</div></div>""",
        unsafe_allow_html=True,
    )
    with st.expander("SHA-256 hashes (minh họa)"):
        st.markdown("**Prompt**")
        st.code(PROMPT_HASH, language="text")
        st.download_button("Sao chép hash Prompt", PROMPT_HASH, file_name="prompt.sha256", key="copy-prompt")
        st.markdown("**Tools**")
        st.code(TOOLS_HASH, language="text")
        st.download_button("Sao chép hash Tools", TOOLS_HASH, file_name="tools.sha256", key="copy-tools")
        st.caption("Đây là metadata minh họa; backend thật sẽ cung cấp hash từ Python.")
        st.caption("Fixture chỉ kiểm tra cách hiển thị, chưa được xác minh với Python/repo smoke test.")

    st.markdown('<div class="sidebar-section"><span class="eyebrow">TRANSCRIPT</span></div>', unsafe_allow_html=True)
    transcript_kind = "Transcript mẫu" if st.session_state.tab == "samples" else "Lịch sử thử nhập"
    st.markdown(f'<p class="path">{transcript_kind} — tải về máy</p>', unsafe_allow_html=True)
    st.markdown('<div class="saved"><span>✓</span> JSON minh họa trong trình duyệt</div>', unsafe_allow_html=True)

    if st.session_state.tab == "samples":
        transcript = sample_transcript(st.session_state.fixture_key, st.session_state.session)
        filename = f"transcript-mau-{st.session_state.session}.json"
    else:
        transcript = try_transcript(st.session_state.messages, st.session_state.session)
        filename = f"lich-su-thu-nhap-{st.session_state.session}.json"
    st.download_button(
        f"⇩ Tải {transcript_kind.lower()}",
        data=json_text(transcript),
        file_name=filename,
        mime="application/json",
        use_container_width=True,
        key="download-transcript",
    )
    st.markdown('<div class="sidebar-footer"><span class="preview-pill">PREVIEW</span><span>Dữ liệu minh họa</span></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Header and main workspace
# ---------------------------------------------------------------------------

st.markdown(
    """<header class="topbar"><div><span class="eyebrow">NORTHSTAR LABS / IT OPERATIONS</span>
    <h1>IT Helpdesk Agent</h1><p>Tra cứu dịch vụ, kiểm tra thiết bị và hỗ trợ sự cố IT</p></div>
    <div class="connection"><span class="connection-dot"></span>Preview sẵn sàng · Backend chưa kết nối
    <span class="mock-badge">Bản xem trước — dữ liệu minh họa</span></div></header>""",
    unsafe_allow_html=True,
)

# Streamlit buttons provide the same two-mode tab behavior while keeping the
# active mode in session state so the sidebar download always matches the view.
mode_col1, mode_col2 = st.columns(2)
with mode_col1:
    if st.button("Kịch bản mẫu", type="primary" if st.session_state.tab == "samples" else "secondary", use_container_width=True, key="mode-samples"):
        st.session_state.tab = "samples"
        st.rerun()
with mode_col2:
    if st.button("Thử nhập", type="primary" if st.session_state.tab == "try" else "secondary", use_container_width=True, key="mode-try"):
        st.session_state.tab = "try"
        st.rerun()

if st.session_state.tab == "samples":
    keys = list(FIXTURES.keys())
    selected = st.selectbox(
        "Chọn kịch bản",
        options=keys,
        index=keys.index(st.session_state.fixture_key),
        format_func=lambda key: FIXTURES[key].label,
        key="fixture-select",
    )
    if selected != st.session_state.fixture_key:
        st.session_state.fixture_key = selected
        st.rerun()
    fixture = FIXTURES[st.session_state.fixture_key]
    st.markdown(
        f'<div class="sample-bar"><span class="eyebrow">KỊCH BẢN</span><span class="status-chip">{html.escape(fixture.status)}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<section class="panel"><div class="conversation">', unsafe_allow_html=True)
    if fixture.opening:
        render_message("user", fixture.opening, "Người dùng", "sample-user")
    if fixture.assistant:
        render_message("assistant", fixture.assistant, "Northstar Agent · dữ liệu minh họa", "sample-assistant")
        render_trace(fixture.events, f"sample-{st.session_state.fixture_key}")
    else:
        st.markdown(
            '<div class="empty-state"><strong>Chưa có hội thoại</strong><span>Chọn một kịch bản có tool trace để xem transcript mẫu.</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div></section>', unsafe_allow_html=True)

else:
    st.markdown(
        '<section class="panel try-panel"><div class="try-heading"><div><span class="eyebrow">LOCAL PREVIEW</span><h2>Lịch sử thử nhập</h2></div><span class="status-chip">Chưa gửi tới agent thật</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="try-history">', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown(
            '<div class="empty-state"><strong>Chưa có tin nhắn thử</strong><span>Nhập yêu cầu bên dưới để xem phản hồi mô phỏng.</span></div>',
            unsafe_allow_html=True,
        )
    else:
        for index, message in enumerate(st.session_state.messages):
            role = "user" if message["role"] == "user" else "assistant"
            label = "Người dùng" if role == "user" else "Northstar Agent · dữ liệu minh họa"
            render_message(role, message["text"], label, f"try-{index}")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.clear_input:
        # Clear the widget on the rerun after submission; Streamlit forbids
        # mutating a widget's state after that widget has been instantiated.
        st.session_state.input_text_widget = ""
        st.session_state.clear_input = False
    st.text_area(
        "Nội dung yêu cầu",
        key="input_text_widget",
        placeholder="Ví dụ: kiểm tra trạng thái Wi-Fi production…",
        label_visibility="collapsed",
        height=90,
    )
    col_send, col_note = st.columns([1, 3])
    with col_send:
        if st.button("Gửi thử", type="primary", use_container_width=True, key="send-message"):
            send_message()
            st.rerun()
    with col_note:
        st.caption("Enter để gửi · Shift+Enter xuống dòng")
    st.markdown('</section>', unsafe_allow_html=True)
