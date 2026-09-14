# Local web UI

The UI reuses `chat.run_model_tool_loop` and shows every round, tool name,
arguments, result/error, status, provider/model, and artifact version. Transcripts
are written to `evidence/transcripts/`, which is intentionally outside the ignored
runtime `transcripts/` directory so selected sanitized evidence can be submitted.

From `starter_v0/`:

```powershell
python ui.py --provider openai --version v3
```

Open <http://127.0.0.1:8000>. Press `Ctrl+C` in the terminal to stop the server.

Do not enter real passwords, API keys, MFA/OTP values, recovery codes, or personal
data. Review generated transcripts before committing them.
