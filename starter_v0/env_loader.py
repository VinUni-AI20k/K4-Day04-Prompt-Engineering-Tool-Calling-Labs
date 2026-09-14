from __future__ import annotations

import os
from pathlib import Path


ENV_ALIASES = {
    "OPENAI_API_KEY": ["ENV_OPENAI", "OPENAI_KEY"],
    "OPENROUTER_API_KEY": ["ENV_OPENROUTER", "OPENROUTER_KEY"],
    "ANTHROPIC_API_KEY": ["ENV_ANTHROPIC", "ANTHROPIC_KEY"],
    "GEMINI_API_KEY": ["ENV_GEMINI", "GEMINI_KEY", "GOOGLE_API_KEY"],
}


def load_dotenv(path: Path, *, override: bool = True) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and (override or key not in os.environ):
            os.environ[key] = value


def apply_env_aliases() -> None:
    for canonical, aliases in ENV_ALIASES.items():
        if os.getenv(canonical):
            continue
        for alias in aliases:
            value = os.getenv(alias)
            if value:
                os.environ[canonical] = value
                break


def load_lab_env(root: Path) -> None:
    external_path = os.getenv("DAY04_ENV_FILE")
    if external_path:
        load_dotenv(Path(external_path).expanduser())
        apply_env_aliases()
        return
    load_dotenv(root / ".env", override=False)
    load_dotenv(root.parent / ".env", override=False)
    apply_env_aliases()
