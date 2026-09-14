---
name: clarify
track: core
kind: control
requires_env: []
inputs: [question, response_type, options]
outputs: [tool, question, response_type, options, awaiting_user]
side_effect: false
---
# clarify

Returns a question to the user and pauses until the next user turn. This is a
control tool with no data access or side effect. `response_type` is `text`,
`yes_no`, or `choice`; `options` supplies labels for `choice`.
