from __future__ import annotations

import argparse
import json
import re
import threading
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from chat import run_model_tool_loop, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
UI_DIR = ROOT / "ui"
EVIDENCE_DIR = ROOT / "evidence" / "transcripts"
load_lab_env(ROOT)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_session_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-._")
    return (cleaned or "session")[:80]


class HelpdeskWebApp:
    def __init__(
        self,
        *,
        provider_name: str,
        model: str | None,
        version: str,
        system_prompt_path: Path,
        tools_path: Path,
        max_tool_rounds: int,
        history_window: int,
    ) -> None:
        self.provider_name = provider_name
        self.provider = make_provider(provider_name)
        self.model = model
        self.selected_model = model or getattr(self.provider, "default_model", None)
        self.system_prompt_path = system_prompt_path
        self.tools_path = tools_path
        self.system_prompt = system_prompt_path.read_text(encoding="utf-8")
        self.tools = to_openai_tools(load_tool_declarations(tools_path))
        self.artifact = build_artifact_version(version, system_prompt_path, tools_path)
        self.max_tool_rounds = max_tool_rounds
        self.history_window = history_window
        self.sessions: dict[str, dict[str, Any]] = {}
        self.lock = threading.Lock()

    def public_config(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "model": self.selected_model,
            **artifact_version_dict(self.artifact),
            "max_tool_rounds": self.max_tool_rounds,
        }

    def _new_session(self, session_id: str) -> dict[str, Any]:
        return {
            "session_id": session_id,
            **self.public_config(),
            "system_prompt": str(self.system_prompt_path),
            "tools": str(self.tools_path),
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
            "history": [],
        }

    def chat(self, session_id: str, user_text: str) -> dict[str, Any]:
        session_id = safe_session_id(session_id)
        user_text = user_text.strip()
        if not user_text:
            raise ValueError("message must not be empty")
        if len(user_text) > 10_000:
            raise ValueError("message exceeds 10000 characters")

        with self.lock:
            session = self.sessions.setdefault(session_id, self._new_session(session_id))
            history = list(session["history"])

        messages = [
            {"role": "system", "content": self.system_prompt},
            *trim_history(history, self.history_window),
            {"role": "user", "content": user_text},
        ]
        started_at = now_iso()
        result = run_model_tool_loop(
            provider=self.provider,
            messages=messages,
            tools=self.tools,
            model=self.model,
            max_tool_rounds=self.max_tool_rounds,
        )
        turn = {
            "turn_index": len(session["turns"]) + 1,
            "started_at": started_at,
            "ended_at": now_iso(),
            "user": user_text,
            **result,
        }

        with self.lock:
            session["turns"].append(turn)
            session["history"].extend(
                [
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": result["assistant_text"]},
                ]
            )
            session["updated_at"] = now_iso()
            self._write_transcript(session)

        return {**self.public_config(), **turn}

    def _write_transcript(self, session: dict[str, Any]) -> None:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        payload = {key: value for key, value in session.items() if key != "history"}
        path = EVIDENCE_DIR / f"{session['session_id']}.transcript.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def make_handler(app: HelpdeskWebApp) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "NorthstarHelpdesk/1.0"

        def _json(self, payload: Any, status: int = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _static(self, filename: str, content_type: str) -> None:
            path = UI_DIR / filename
            if not path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            body = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            if self.path in {"/", "/index.html"}:
                self._static("index.html", "text/html; charset=utf-8")
            elif self.path == "/app.js":
                self._static("app.js", "text/javascript; charset=utf-8")
            elif self.path == "/styles.css":
                self._static("styles.css", "text/css; charset=utf-8")
            elif self.path == "/api/health":
                self._json({"status": "ok", **app.public_config()})
            else:
                self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
            if self.path != "/api/chat":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 20_000:
                    raise ValueError("invalid request size")
                data = json.loads(self.rfile.read(length).decode("utf-8"))
                result = app.chat(str(data.get("session_id", "session")), str(data.get("message", "")))
                self._json(result)
            except (ValueError, json.JSONDecodeError) as exc:
                self._json({"error": type(exc).__name__, "message": str(exc)}, HTTPStatus.BAD_REQUEST)
            except Exception as exc:  # keep provider errors visible to the UI
                self._json({"error": type(exc).__name__, "message": str(exc)}, HTTPStatus.BAD_GATEWAY)

        def log_message(self, fmt: str, *args: Any) -> None:
            print(f"[ui] {self.address_string()} {fmt % args}")

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Local web UI for the IT Helpdesk Agent.")
    parser.add_argument("--provider", choices=["openai", "openrouter", "anthropic", "gemini"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", default="v3")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    args = parser.parse_args()

    app = HelpdeskWebApp(
        provider_name=args.provider,
        model=args.model,
        version=args.version,
        system_prompt_path=args.system_prompt,
        tools_path=args.tools,
        max_tool_rounds=args.max_tool_rounds,
        history_window=args.history_window,
    )
    server = ThreadingHTTPServer((args.host, args.port), make_handler(app))
    print(f"Northstar Helpdesk UI: http://{args.host}:{args.port}")
    print(f"artifact_version={app.artifact.artifact_version}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping UI.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
