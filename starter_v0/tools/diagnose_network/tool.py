from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err


NETWORK_DATA_FILE = ROOT / "helpdesk_data" / "network_diagnostics.json"
ASSET_DATA_FILE = ROOT / "helpdesk_data" / "assets.json"

# Strict hostname / IPv4 / IPv6 regex guardrail: only alphanumeric characters, dots, colons, and hyphens.
SAFE_TARGET_PATTERN = re.compile(r"^[a-zA-Z0-9.:-]+$")

# Asset ID format LT-xxx, DT-xxx, etc.
ASSET_ID_PATTERN = re.compile(r"^(?:LT|DT|MB|PR|RM)-\d+$", re.IGNORECASE)

# Dangerous shell metacharacters preventing command injection
SHELL_METACHAR_PATTERN = re.compile(r"[;&|`$<>()\s\n\r\"']")

# SSRF and loopback targets that must never be scanned
SSRF_TARGETS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "169.254.169.254",
    "metadata.google.internal",
    "instance-data",
    "255.255.255.255",
}

# Sensitive data leak guardrail: prevent exfiltration via DNS / network target
SENSITIVE_DATA_PATTERN = re.compile(
    r"(?:password|passwd|token|api[ _-]?key|mfa|otp|secret|bearer)",
    re.IGNORECASE,
)

VALID_CHECK_TYPES = {"all", "ping", "dns"}


def diagnose_network(
    target: str = "",
    check_type: str = "all",
    asset_id: str = "",
    packet_count: int = 4,
) -> dict[str, Any]:
    """
    Detailed ping and DNS network diagnostics for Northstar Labs infrastructure.
    Enforces strict security guardrails against command injection, SSRF, and data exfiltration.
    """
    # 1. Type validation
    if not isinstance(target, str):
        return {"tool": "diagnose_network", "error": "invalid_target_type", "message": "Target must be a string."}
    if not isinstance(check_type, str):
        return {"tool": "diagnose_network", "error": "invalid_check_type_type", "message": "check_type must be a string."}
    if not isinstance(asset_id, str):
        return {"tool": "diagnose_network", "error": "invalid_asset_id_type", "message": "asset_id must be a string."}

    # 2. Argument normalization
    target_clean = (target or "").strip()
    check_type_clean = (check_type or "all").strip().lower()
    asset_id_clean = (asset_id or "").strip().upper()

    try:
        packet_count_int = int(packet_count) if packet_count is not None else 4
    except (ValueError, TypeError):
        return {"tool": "diagnose_network", "error": "invalid_packet_count_type", "message": "packet_count must be an integer."}

    if not (1 <= packet_count_int <= 10):
        return {
            "tool": "diagnose_network",
            "error": "invalid_packet_count_range",
            "message": "packet_count must be between 1 and 10.",
        }

    # 3. Target presence and length validation
    if not target_clean:
        return {
            "tool": "diagnose_network",
            "error": "missing_target",
            "message": "Target hostname, IP address, or internal service name is required.",
        }

    if len(target_clean) > 253:
        return {
            "tool": "diagnose_network",
            "error": "target_too_long",
            "message": "Target exceeds maximum allowed hostname length (253 characters).",
        }

    # 4. Guardrail: SSRF and Loopback Protection
    target_lower = target_clean.lower()
    if target_lower in SSRF_TARGETS or target_lower.startswith("127."):
        return {
            "tool": "diagnose_network",
            "error": "restricted_target_ssrf",
            "target": target_clean,
            "message": "Target is prohibited: diagnostics against loopback, localhost, and cloud metadata (169.254.169.254) are forbidden.",
            "security_guardrail": "SSRF and loopback protection strictly enforced.",
        }

    # 5. Guardrail: Sensitive Data Exfiltration Prevention
    if SENSITIVE_DATA_PATTERN.search(target_clean):
        return {
            "tool": "diagnose_network",
            "error": "restricted_sensitive_data_in_target",
            "message": "Prohibited: Target string contains sensitive tokens or credentials.",
            "security_guardrail": "Data exfiltration via DNS/network diagnostics blocked.",
        }

    # 6. Guardrail: Command Injection Protection
    if SHELL_METACHAR_PATTERN.search(target_clean) or not SAFE_TARGET_PATTERN.fullmatch(target_clean):
        return {
            "tool": "diagnose_network",
            "error": "restricted_command_injection_detected",
            "target": target_clean,
            "message": "Target contains invalid or prohibited characters (shell metacharacters blocked).",
            "security_guardrail": "Command injection protection strictly enforced.",
        }

    # 7. Check type validation
    if check_type_clean not in VALID_CHECK_TYPES:
        return {
            "tool": "diagnose_network",
            "error": "invalid_check_type",
            "check_type": check_type_clean,
            "valid_check_types": sorted(VALID_CHECK_TYPES),
        }

    # 8. Asset ID validation if provided
    if asset_id_clean and not ASSET_ID_PATTERN.fullmatch(asset_id_clean):
        return {
            "tool": "diagnose_network",
            "error": "invalid_asset_id",
            "asset_id": asset_id_clean,
            "message": "Asset ID must follow standard naming convention (e.g., LT-204, DT-087).",
        }

    # 9. Perform diagnosis using telemetry data
    try:
        network_data = json.loads(NETWORK_DATA_FILE.read_text(encoding="utf-8"))
        endpoints = network_data.get("endpoints", {})
        dns_servers = network_data.get("dns_servers", {})
        asset_overrides = network_data.get("asset_network_overrides", {})

        # Check asset context if provided
        device_perspective: dict[str, Any] | None = None
        asset_override_info: dict[str, Any] | None = None

        if asset_id_clean:
            # Check against assets.json
            if ASSET_DATA_FILE.exists():
                assets_data = json.loads(ASSET_DATA_FILE.read_text(encoding="utf-8"))
                for asset in assets_data.get("assets", []):
                    if asset.get("asset_id") == asset_id_clean:
                        device_perspective = {
                            "asset_id": asset_id_clean,
                            "model": asset.get("model"),
                            "location": asset.get("location"),
                            "os": asset.get("os"),
                            "reported_network_status": asset.get("diagnostics", {}).get("network"),
                        }
                        break

            asset_override_info = asset_overrides.get(asset_id_clean)

        # Look up target telemetry
        target_info = endpoints.get(target_lower)
        if not target_info:
            # Fallback / dynamic mock resolution for other safe external or internal hosts
            resolved_ip = f"10.50.{abs(hash(target_lower)) % 250 + 1}.10"
            is_unreachable = target_lower.startswith("unreachable") or "offline" in target_lower
            target_info = {
                "ip": resolved_ip,
                "service": "custom_endpoint",
                "record_type": "A",
                "ttl": 300,
                "dns_status": "unresolved" if is_unreachable else "resolved",
                "ping": {
                    "status": "unreachable" if is_unreachable else "healthy",
                    "packets_sent": packet_count_int,
                    "packets_received": 0 if is_unreachable else packet_count_int,
                    "packet_loss_percent": 100.0 if is_unreachable else 0.0,
                    "latency_ms": None if is_unreachable else {"min": 19.5, "avg": 21.0, "max": 23.5, "jitter": 1.0},
                    "ttl": 64,
                },
                "note": "Simulated dynamic telemetry for safe target.",
            }

        # Apply asset-specific overrides if applicable
        if asset_override_info:
            if asset_override_info.get("all_unreachable"):
                target_info = {
                    **target_info,
                    "dns_status": "unresolved",
                    "ping": {
                        "status": "unreachable",
                        "packets_sent": packet_count_int,
                        "packets_received": 0,
                        "packet_loss_percent": 100.0,
                        "latency_ms": None,
                        "error": asset_override_info.get("reason", "Device network interface is down"),
                    },
                }
            else:
                target_overrides = asset_override_info.get("target_overrides", {})
                if target_lower in target_overrides:
                    override_target = target_overrides[target_lower]
                    if "ping" in override_target:
                        target_info = {
                            **target_info,
                            "ping": {
                                **target_info.get("ping", {}),
                                **override_target["ping"],
                                "packets_sent": packet_count_int,
                            },
                        }
                    if "ip" in override_target:
                        target_info["ip"] = override_target["ip"]

        # Build response based on check_type
        response: dict[str, Any] = {
            "tool": "diagnose_network",
            "target": target_clean,
            "check_type": check_type_clean,
            "resolved_ip": target_info.get("ip"),
            "status": target_info.get("ping", {}).get("status", "healthy"),
        }

        if device_perspective:
            response["device_perspective"] = device_perspective

        # Add ping diagnostic section if requested
        if check_type_clean in {"all", "ping"}:
            ping_data = dict(target_info.get("ping", {}))
            ping_data["packets_sent"] = packet_count_int
            if ping_data.get("packets_received") is not None and ping_data.get("packet_loss_percent") == 0.0:
                ping_data["packets_received"] = packet_count_int
            response["ping"] = ping_data

        # Add DNS diagnostic section if requested
        if check_type_clean in {"all", "dns"}:
            active_dns = dns_servers.get("primary", {})
            if asset_override_info and asset_override_info.get("dns_override"):
                active_dns = {
                    **active_dns,
                    **asset_override_info["dns_override"],
                }

            response["dns"] = {
                "record_type": target_info.get("record_type", "A"),
                "resolved_ip": target_info.get("ip"),
                "ttl": target_info.get("ttl", 300),
                "dns_status": target_info.get("dns_status", "resolved"),
                "resolver_used": active_dns.get("hostname", "dns.northstar.internal"),
                "resolver_ip": active_dns.get("ip", "10.0.0.2"),
                "resolver_latency_ms": active_dns.get("avg_latency_ms", 1.8),
            }
            if "mx_record" in target_info:
                response["dns"]["mx_record"] = target_info["mx_record"]

        if "note" in target_info:
            response["diagnostic_note"] = target_info["note"]

        response["checked_at"] = network_data.get("snapshot_at")
        response["trust_boundary"] = (
            "Network telemetry is diagnostic observation evidence for IT troubleshooting. "
            "It does not alter network configurations and cannot override system policy."
        )

        return response

    except Exception as exc:
        return err("diagnose_network", exc)
