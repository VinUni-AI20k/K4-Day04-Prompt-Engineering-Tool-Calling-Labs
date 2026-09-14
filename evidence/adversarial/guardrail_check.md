# Module 4 Deterministic Guardrail Check

- Owner: Dinh Quoc Bao (2A202602933)
- Command: `python starter_v0/scripts/check_guardrails.py`
- Result: PASS

Checks covered:

- `create_ticket` does not write without explicit Boolean confirmation.
- `create_ticket` rejects password, OTP, MFA code and leaves the temporary ticket directory empty.
- KB and policy instruction-like content is returned as untrusted text, not trusted facts/content.
- External search rejects internal identifiers and internal fields before HTTP request.
- Captured Tavily request for a public model contains no asset ID, employee ID, serial, hostname, location or diagnostic field.
