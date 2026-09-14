---
name: search_device_info
track: bonus
kind: live_api
provider: Tavily Search API
requires_env: [TAVILY_API_KEY]
inputs: [manufacturer, model, query_type, max_results]
outputs: [tool, manufacturer, model, query_type, query, official_domains, items, external_data_notice, trust_boundary]
side_effect: false
---
# search_device_info

Searches public product specifications, drivers, compatibility information, or
vendor support pages for a known manufacturer and model. Inputs must contain
public product data only. Never send asset IDs, employee IDs, diagnostic logs,
hostnames, serial numbers, credentials, or other internal data to this tool.
`max_results` is capped at 5 and results include separated `untrusted_text`.
Missing `TAVILY_API_KEY`, restricted identifiers, invalid query types, or
invalid public identity return an error object without an external request.
The tool sends public identity to Tavily and has no local write side effect.
Results outside the known vendor allowlist are filtered when an allowlist is
available. Instruction-like result text is separated and never trusted.
