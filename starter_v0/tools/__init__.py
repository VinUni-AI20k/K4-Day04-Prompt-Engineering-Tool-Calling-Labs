from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .clarify.tool import ask_user
from .check_service_status.tool import check_service_status
from .create_ticket.tool import create_ticket
from .format_incident_report.tool import format_incident_report
from .inspect_device.tool import inspect_device
from .lookup_user.tool import lookup_user
from .policy.tool import search_company_policy
from .search_kb.tool import search_kb
from .search_device_info.tool import search_device_info


# NOTE (starter_v0): these keys are the names the model sees AND the names
# data/eval_base.json + data/eval_helpdesk_extension.json
# match against. If a team renames a tool, it MUST stay in sync across ALL of:
#   artifacts/tools.yaml  ->  this dict  ->  data/eval_base.json + data/eval_helpdesk_extension.json
# Otherwise the eval raises "not declared in tools.yaml" or scores every call as a name mismatch.
TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "search_kb": search_kb,
    "search_device_info": search_device_info,
    "check_service_status": check_service_status,
    "inspect_device": inspect_device,
    "lookup_user": lookup_user,
    "format_incident_report": format_incident_report,
    "policy": search_company_policy,
    "create_ticket": create_ticket,
}


def load_tool_declarations(path: Path) -> list[dict[str, Any]]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))["tools"]


def to_openai_tools(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    openai_tools = []
    for item in declarations:
        desc_parts = [item.get("description", "")]
        
        if "when_to_use" in item:
            desc_parts.append("\nWHEN TO USE:\n- " + "\n- ".join(item["when_to_use"]))
        if "when_NOT_to_use" in item:
            desc_parts.append("\nWHEN NOT TO USE:\n- " + "\n- ".join(item["when_NOT_to_use"]))
        if "boundaries" in item:
            desc_parts.append("\nBOUNDARIES:")
            for k, v in item["boundaries"].items():
                desc_parts.append(f"- {k}: {v}")
                
        full_desc = "\n".join(desc_parts).strip()
        
        openai_tools.append({
            "type": "function",
            "function": {
                "name": item["name"],
                "description": full_desc,
                "parameters": item.get("parameters", {"type": "object", "properties": {}}),
            },
        })
    return openai_tools
