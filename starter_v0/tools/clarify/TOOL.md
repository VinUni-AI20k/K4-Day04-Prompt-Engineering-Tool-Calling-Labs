---
name: clarify
track: core
kind: control
requires_env: []
inputs: [question, response_type, options]
outputs: [question, response_type, options, awaiting_user]
side_effect: false
---
# clarify

Returns a question to the user and pauses until the next user turn.
`response_type` is free text, yes/no, or a choice from `options`.

Use it for a missing required identifier, an ambiguous/unsupported enum, a
clean public manufacturer/model request before external search, or exact
payload confirmation before a side effect. Do not use it to reconfirm a
complete read-only request, and never repeat a secret in its arguments.
