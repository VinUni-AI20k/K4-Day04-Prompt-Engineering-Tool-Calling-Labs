# Runbook for the completed lab scaffold

The repository contains a final draft prompt, improved tool declarations, 10
team-authored group cases, a Streamlit UI, a report scaffold, and a version
ledger. Live evidence, real team identity, Git history, and VLearn submission
remain pending because they require the team's provider key and accounts.

## Repair Python

The current `.venv` executable is blocked and the `py` launcher reports no
installed Python. Install Python 3.10 or later, reopen PowerShell, then run:

```powershell
py -3 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If activation remains blocked, invoke `.\.venv\Scripts\python.exe` directly
instead of `python`; do not change the system-wide execution policy.

## Configure and validate the provider

Copy `.env.example` to `.env`, set exactly one provider API key, and never
commit `.env`. Add `TAVILY_API_KEY` only for external-search evidence.

```powershell
Copy-Item .env.example .env
python scripts/preflight_provider.py --provider openrouter
```

## Generate genuine evidence

Run v0 before the final root artifacts. Copy generated JSON from ignored
`runs/` into a committed evidence directory, then replace every pending value
in `artifacts/version_log.csv` and `artifacts/REPORT.md` with observed output.

```powershell
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json --system-prompt artifacts/versions/v0/system_prompt.md --tools artifacts/versions/v0/tools.yaml
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
python run_eval.py --provider openrouter --version v3 --suite extension --eval-cases data/eval_helpdesk_extension.json
python run_eval.py --provider openrouter --version v3 --suite adversarial --eval-cases data/eval_adversarial.json
python scripts/parse_runs.py runs --output analysis/run-analysis.csv
```

An evidence metric is valid only when `provider_error_cases` is zero and
`measured_cases` equals `total_cases`. Inspect tool results and the filesystem.

## Run the UI

```powershell
streamlit run app.py
```

The UI reuses `chat.run_model_tool_loop`, shows tool traces and hashes, and
saves transcripts. Copy selected sanitized transcripts to committed evidence.

## Submit as a team

Fill `TEAMMATES.md`, fork the source repository, ensure every member has a
non-squashed merged commit, complete the report from real evidence, and submit
the same fork URL from every VLearn account.
