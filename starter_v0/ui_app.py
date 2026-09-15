from __future__ import annotations

import json
import os
import queue
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from chat import now_iso, run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS = ROOT / "artifacts"
WEB = ROOT / "web"
TRANSCRIPTS = ROOT / "transcripts"
REHEARSALS = ROOT / "evidence" / "transcripts"
load_lab_env(ROOT)

app = FastAPI(title="Northstar Operations Console")
app.mount("/assets", StaticFiles(directory=WEB), name="assets")


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    history: list[HistoryItem] = Field(default_factory=list)
    provider: Literal["openai", "openrouter", "anthropic", "gemini"] = "openai"
    model: str | None = Field(default=None, max_length=180)
    conversation_id: str | None = Field(default=None, max_length=80)


def artifact() -> dict[str, str]:
    return artifact_version_dict(build_artifact_version("v3", ARTIFACTS / "system_prompt.md", ARTIFACTS / "tools.yaml"))


def available_providers() -> dict[str, bool]:
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
    }


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB / "index.html")


@app.get("/api/bootstrap")
def bootstrap() -> dict[str, Any]:
    rehearsals = []
    for path in sorted(REHEARSALS.glob("*.transcript.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rehearsals.append({"id": data["transcript_id"], "title": data.get("scenario_title", data["transcript_id"])})
    return {"artifact": artifact(), "providers": available_providers(), "tools": [tool["name"] for tool in load_tool_declarations(ARTIFACTS / "tools.yaml")], "rehearsals": rehearsals}


@app.get("/api/rehearsals/{transcript_id}")
def rehearsal(transcript_id: str) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", transcript_id):
        raise HTTPException(status_code=404, detail="Rehearsal not found.")
    path = REHEARSALS / f"{transcript_id}.transcript.json"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Rehearsal not found.")
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/api/chat")
def chat(request: ChatRequest) -> StreamingResponse:
    if not available_providers()[request.provider]:
        raise HTTPException(status_code=400, detail=f"Provider {request.provider} chưa được cấu hình.")
    conversation_id = request.conversation_id if request.conversation_id and re.fullmatch(r"[A-Za-z0-9_-]+", request.conversation_id) else uuid4().hex
    provider = make_provider(request.provider)
    model = request.model or getattr(provider, "default_model", None)
    prompt = (ARTIFACTS / "system_prompt.md").read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(ARTIFACTS / "tools.yaml"))
    messages = [{"role": "system", "content": prompt}, *trim_history([item.model_dump() for item in request.history], 5), {"role": "user", "content": request.message}]
    events: queue.Queue[dict[str, Any] | None] = queue.Queue()

    def worker() -> None:
        try:
            result = run_model_tool_loop(provider=provider, messages=messages, tools=tools, model=request.model, max_tool_rounds=4, on_event=events.put)
            transcript_path = TRANSCRIPTS / f"{conversation_id}.transcript.json"
            if transcript_path.exists():
                transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
            else:
                transcript = {"transcript_id": conversation_id, **artifact(), "provider": request.provider, "model": model, "created_at": now_iso(), "turns": []}
            transcript["turns"].append({"started_at": now_iso(), "user": request.message, **result, "ended_at": now_iso()})
            write_transcript(transcript_path, transcript)
            events.put({"type": "transcript_saved", "transcript_id": conversation_id, "artifact": artifact(), "provider": request.provider, "model": model})
        except Exception as exc:
            events.put({"type": "error", "message": f"{type(exc).__name__}: {exc}"})
        finally:
            events.put(None)

    threading.Thread(target=worker, daemon=True).start()

    def stream() -> Any:
        yield json.dumps({"type": "connected", "conversation_id": conversation_id, "artifact": artifact(), "provider": request.provider, "model": model}, ensure_ascii=False) + "\n"
        while (event := events.get()) is not None:
            yield json.dumps(event, ensure_ascii=False, default=str) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ui_app:app", host="127.0.0.1", port=8000, reload=True)
