python --version# Zone A — Prompt evidence runbook

This runbook preserves evidence for the Prompt Architect / Lead scope. It does
not permit invented metrics: copy a metric or run path only from a run JSON
whose `provider_error_cases` is `0` and whose `measured_cases` equals
`total_cases`.

## 1. Check the local runtime

Run these from `starter_v0/`. The provider is OpenRouter when
`OPENROUTER_API_KEY` is configured in the local `.env`; never print or commit
that file.

```powershell
python -m compileall -q .
python -m unittest discover -s tests -v
python scripts/preflight_provider.py --provider openrouter
```

## 2. Produce comparable base runs

Keep `tools.yaml` unchanged across these four runs. Each command records the
artifact hashes in the generated JSON.

```powershell
python run_eval.py --provider openrouter --version v0 --suite base --system-prompt artifacts/versions/v0/system_prompt.md --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v1 --suite base --system-prompt artifacts/versions/v1/system_prompt.md --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v2 --suite base --system-prompt artifacts/versions/v2/system_prompt.md --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite base --system-prompt artifacts/versions/v3/system_prompt.md --eval-cases data/eval_base.json
```

Copy the exact output path and metric values into `artifacts/version_log.csv`
and `artifacts/REPORT.md`. Do not replace a pending value until the run is
valid.

## 3. Capture carry-over and action-boundary evidence

```powershell
python chat.py --provider openrouter --version v3
```

Save separate transcripts for:

1. A normal read-only request.
2. A missing asset ID or environment, followed by the answer.
3. A corrected identifier or cancellation.
4. A ticket whose priority changes before a fresh yes/no confirmation.

For each transcript, confirm the tool trace shows the latest intent, no stale
confirmation, the final-response JSON validation, and the displayed artifact
version/hash.

## 4. Security regression evidence

After base routing is stable, run the fixed adversarial suite and manually
review at least three cases. Inspect `tool_results` and the filesystem; a tool
call score alone does not prove that no write or external-data disclosure
occurred.

```powershell
python run_eval.py --provider openrouter --version v3 --suite adversarial --eval-cases data/eval_adversarial.json
```

Do not commit `.env`, `tickets/`, secrets, or real data. Commit only the
sanitized run/transcript evidence required by the lab.
