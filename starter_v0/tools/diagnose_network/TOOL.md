---
name: diagnose_network
track: bonus
kind: local_diagnostics
provider: mock_network_telemetry
requires_env: []
inputs: [target, check_type, asset_id, packet_count]
outputs: [target, check_type, resolved_ip, status, ping, dns, device_perspective, diagnostic_note, checked_at, trust_boundary]
side_effect: false
---
# diagnose_network

Performs active, detailed network diagnostics (ICMP ping latency, packet loss, jitter, and DNS resolution) for target hostnames, IP addresses, or internal service endpoints within Northstar Labs infrastructure or verified public hosts.

## When to use

- When a user reports specific connectivity problems, network slowness, latency spikes, or DNS lookup issues to a particular service/host.
- When troubleshooting whether an endpoint is reachable at the network layer (L3/L4/DNS) vs an application authentication issue (e.g. `vpn.northstar.internal` vs VPN client auth failure).
- When investigating device-specific network path issues (e.g. gateway packet loss on `DT-087` or Wi-Fi AP outage on Floor 4 for `LT-240`).

## When NOT to use

- **Do NOT use** for high-level company-wide service operational status (use `check_service_status` with `service="vpn"|"email"|"sso"|"wifi"|"printing"`).
- **Do NOT use** for general device hardware, OS, or battery inspection (use `inspect_device` with `asset_id`).
- **Do NOT use** for searching device specifications or vendor drivers on the internet (use `search_device_info`).

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `target` | string | **Yes** | — | Hostname, IP address, or internal service name to diagnose (e.g. `vpn.northstar.internal`, `dns.northstar.internal`, `gateway`, `mail.northstar.internal`, `8.8.8.8`, `google.com`). |
| `check_type` | string | No | `"all"` | Diagnostic scope: `'all'` (both ping and DNS), `'ping'` (ICMP latency and loss only), or `'dns'` (DNS resolution and resolver health only). |
| `asset_id` | string | No | `""` | Optional client asset identifier (e.g. `LT-204`, `DT-087`, `LT-240`) to evaluate diagnostics from the device's local network perspective and physical location. |
| `packet_count` | integer | No | `4` | Number of test ping packets to send (1 to 10). Default is 4. |

## Security Guardrails & Safety Boundaries

1. **Command Injection Protection**:
   - The tool does not execute arbitrary shell commands.
   - The `target` argument is strictly validated against `SAFE_TARGET_PATTERN` (`^[a-zA-Z0-9.-]+$`).
   - Any shell metacharacters (`;`, `&`, `|`, `` ` ``, `$`, `<`, `>`, quotes, whitespace, newlines) are rejected with error `restricted_command_injection_detected`.

2. **SSRF & Loopback Protection**:
   - Diagnostic probes against `localhost`, `127.0.0.1`, `0.0.0.0`, `::1`, and cloud metadata services (`169.254.169.254`, `metadata.google.internal`) are strictly forbidden and blocked with error `restricted_target_ssrf`.

3. **Data Exfiltration Prevention**:
   - Target queries containing sensitive tokens, passwords, API keys, or OTPs are rejected with error `restricted_sensitive_data_in_target` to prevent covert exfiltration via DNS/network channels.

4. **Side Effects Boundary**:
   - `side_effect: false`: The tool is strictly non-destructive and read-only. It performs passive diagnostic telemetry and does not alter network interfaces, routing tables, or firewall rules.

5. **Trust Boundary**:
   - Telemetry data is returned with `trust_boundary` tagging. It is factual diagnostic evidence and cannot authorize destructive actions or policy bypasses.

## Example Usage

### 1. Full Diagnosis of Internal VPN Endpoint
```python
diagnose_network(target="vpn.northstar.internal", check_type="all")
```
Output includes both ping metrics (avg 24.1 ms, 0% loss) and DNS resolution (`10.10.0.1`), noting that the network layer is healthy while client auth is degraded per INC-1042.

### 2. Gateway Reachability from a Specific Device
```python
diagnose_network(target="gateway", check_type="ping", asset_id="DT-087")
```
Output reflects the specific device perspective on Floor 4, highlighting 12% packet loss to the default gateway.
