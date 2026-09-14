from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import chainlit as cl

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop, now_iso, safe_slug, write_transcript

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"

load_lab_env(ROOT)

def json_text(value: Any, max_chars: int | None = None) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    return text[:max_chars] + "\n...<truncated>" if max_chars and len(text) > max_chars else text

def make_transcript_id(version: str, provider: str) -> str:
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    return "_".join([safe_slug(version), safe_slug(provider), timestamp])

@cl.on_chat_start
async def on_chat_start():
    system_prompt_path, tools_path = ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml"
    provider_name, model, version = "gemini", None, "v0"

    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)

    provider = make_provider(provider_name)
    selected_model = model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)

    transcript_id = make_transcript_id(version, provider_name)
    transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"

    transcript: dict[str, Any] = {
        "transcript_id": transcript_id, **artifact_version_dict(artifact_version),
        "provider": provider_name, "model": selected_model,
        "system_prompt": str(system_prompt_path), "tools": str(tools_path),
        "history_window": 5, "max_tool_rounds": 4, 
        "created_at": now_iso(), "updated_at": now_iso(), "turns": [],
    }

    session_data = {
        "system_prompt": system_prompt, "tool_declarations": tool_declarations,
        "openai_tools": openai_tools, "provider": provider, "model": selected_model,
        "version": version, "history_window": 5, "max_tool_rounds": 4,
        "history": [], "transcript": transcript, "transcript_path": transcript_path
    }
    
    for key, val in session_data.items():
        cl.user_session.set(key, val)

    await cl.Message(
        content=f"# 🤖 IT Helpdesk Agent\n\nAgent đã sẵn sàng.\n\n"
                f"- **Provider:** `{provider_name}`\n- **Model:** `{selected_model}`\n"
                f"- **Artifact:** `{artifact_version.artifact_version}`\n- **Tools:** `{len(tool_declarations)}`\n\n"
                "Mỗi lượt chat sẽ hiển thị **toàn bộ quá trình observable** gồm model response, tool calls, tool arguments, tool results và final answer."
    ).send()

async def render_round(round_record: dict[str, Any]):
    assistant_text = round_record.get("assistant_text", "")
    tool_calls = round_record.get("tool_calls", [])
    tool_results = round_record.get("tool_results", [])

    async with cl.Step(name=f"Round {round_record['round']}", type="run") as step:
        step.output = ""
        if assistant_text:
            step.output += f"### Assistant response\n\n{assistant_text}"
        if tool_calls:
            step.output += f"\n\n### 🔧 Tool Calls\n\n```json\n{json_text(tool_calls)}\n```"
        if tool_results:
            step.output += f"\n\n### 📦 Tool Results\n\n```json\n{json_text(tool_results, max_chars=24000)}\n```"

async def render_final_result(result: dict[str, Any]):
    status = result.get("status")
    status_map = {"answered": "✅ Answered", "waiting_for_user": "⏸️ Waiting for user", "max_tool_rounds": "⚠️ Max tool rounds reached"}
    status_text = status_map.get(status, status or "unknown")

    rounds = result.get("rounds", [])
    total_tools = sum(len(r.get("tool_calls", [])) for r in rounds)

    await cl.Message(content=f"**Status:** {status_text}\n\n**Rounds:** {len(rounds)}\n\n**Tool calls:** {total_tools}").send()
    await cl.Message(author="Agent", content=result.get("assistant_text") or "(empty response)").send()

@cl.on_message
async def on_message(message: cl.Message):
    user_text = message.content.strip()
    if not user_text:
        return

    session = cl.user_session
    sys_prompt, openai_tools = session.get("system_prompt"), session.get("openai_tools")
    provider, model = session.get("provider"), session.get("model")
    history, hw, mtr = session.get("history", []), session.get("history_window", 5), session.get("max_tool_rounds", 4)
    transcript, transcript_path = session.get("transcript"), session.get("transcript_path")

    await cl.Message(author="You", content=user_text).send()

    messages = [{"role": "system", "content": sys_prompt}] + history[-hw * 2:] + [{"role": "user", "content": user_text}]

    turn_record: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1, "started_at": now_iso(),
        "user": user_text, "status": "started", "assistant_text": None,
        "rounds": [], "tool_events": [],
    }

    processing = cl.Message(content="⏳ **Agent đang xử lý...**")
    await processing.send()

    try:
        result = run_model_tool_loop(provider=provider, messages=messages, tools=openai_tools, model=model, max_tool_rounds=mtr)
        await processing.remove()

        for round_record in result.get("rounds", []):
            await render_round(round_record)
        
        await render_final_result(result)

        assistant_text = result.get("assistant_text", "")
        history.extend([{"role": "user", "content": user_text}, {"role": "assistant", "content": assistant_text}])
        session.set("history", history)
        turn_record.update(result)

    except Exception as exc:
        await processing.remove()
        error_message = f"{type(exc).__name__}: {str(exc)}"
        turn_record.update({"status": "provider_error", "error": error_message})
        await cl.Message(author="Agent", content=f"❌ **Agent Error**\n\n```text\n{error_message}\n```").send()

    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    write_transcript(transcript_path, transcript)

    await cl.Message(content=f"💾 Transcript saved:\n`{transcript_path}`").send()

@cl.on_chat_resume
async def on_chat_resume(thread):
    pass