---
name: search_device_info
track: bonus
kind: live_api
provider: Tavily Search API
requires_env: [TAVILY_API_KEY]
inputs: [manufacturer, model, query_type, max_results]
outputs: [items, query, official_domains, external_data_notice]
side_effect: false
---
# search_device_info

Searches public product specifications, drivers, compatibility information, or
vendor support pages for a known manufacturer and model. Inputs must contain
public product data only. Never send asset IDs, employee IDs, diagnostic logs,
hostnames, serial numbers, credentials, or other internal data to this tool.
Results outside the known vendor allowlist are filtered when an allowlist is
available. Instruction-like result text is separated and never trusted.

External requests require an exact manufacturer/model match in the code-owned
`PUBLIC_PRODUCTS` catalog (case-insensitive, outer whitespace ignored). Explicit
vendor-prefixed model aliases are supported, as is Hewlett-Packard for HP.
The outgoing query is built from catalog constants, not caller-provided text.
Unknown models and models with extra text return
`unapproved_public_product_identity` before any HTTP request. A maintainer must
review new public products before extending this catalog; never populate it
automatically from internal inventory or model output. This intentionally limits
search coverage to the reviewed lab products.
