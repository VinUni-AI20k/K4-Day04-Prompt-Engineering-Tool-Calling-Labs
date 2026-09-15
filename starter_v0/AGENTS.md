# AGENTS.md

## Project Overview
This repository implements an AI-powered IT Helpdesk Agent. Agents interact with tools and company policies to handle tickets.

## Workflow & Development

### Running Evaluations
Use `run_eval.py` for all agent evaluation tasks. It supports multiple providers (`openai`, `openrouter`, `anthropic`, `gemini`).

Example command:
```bash
python run_eval.py --version v0_B_base --provider openai --suite base
```

- **Required Args**: `--version`
- **Defaults**:
  - `phase`: B
  - `suite`: base
  - `eval-cases`: `data/eval_base.json`

### Adding Tools
1.  **Structure**: Create `tools/<tool_name>/` containing `TOOL.md` and `tool.py`.
2.  **Registration**: Update `tools/__init__.py` to register the new tool.
3.  **Requirements**: `TOOL.md` must follow the specified frontmatter contract. Only `action` tools should use `requires_confirmation: true`.
4.  **Best Practices**: Use fake data, stable JSON output, and include smoke tests. Never use real credentials or PII.

### Company Policies
Policies are stored in `company_policy/`. Agents must access these ONLY via the `policy()` tool call to ensure they are retrieved as reference context.

## Environment Setup
- `.env`: Contains API keys (see `.env.example`).
- Ensure `requirements.txt` dependencies are installed.
