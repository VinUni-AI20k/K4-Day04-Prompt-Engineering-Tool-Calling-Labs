from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from unittest.mock import Mock

from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from tools.clarify.tool import ask_user
from tools.check_service_status.tool import check_service_status
from tools.create_ticket.tool import create_ticket
from tools.format_incident_report.tool import format_incident_report
from tools.inspect_device.tool import inspect_device
from tools.lookup_user.tool import lookup_user
from tools.policy.tool import search_company_policy
from tools.search_kb.tool import search_kb
from tools.search_device_info.tool import search_device_info


ROOT = Path(__file__).resolve().parents[1]


class ToolContractTests(unittest.TestCase):
    def test_declarations_match_registry_and_signatures(self) -> None:
        declarations = load_tool_declarations(ROOT / "artifacts" / "tools.yaml")
        declared_names = {item["name"] for item in declarations}
        self.assertEqual(declared_names, set(TOOL_FUNCTIONS))
        self.assertEqual(len(declarations), 9)
        for declaration in declarations:
            parameters = declaration["parameters"]
            self.assertEqual(parameters["type"], "object")
            self.assertTrue(set(parameters.get("required", [])) <= set(parameters["properties"]))
        provider_tools = to_openai_tools(declarations)
        self.assertEqual({item["function"]["name"] for item in provider_tools}, declared_names)
        self.assertTrue(all(item["type"] == "function" for item in provider_tools))

    def test_local_tools_return_expected_results_and_unknown_ids(self) -> None:
        self.assertTrue(ask_user("Need asset ID", "text")["awaiting_user"])
        status = check_service_status("vpn", "production")
        self.assertEqual(status["service"], "vpn")
        self.assertEqual(check_service_status("not-a-service", "production")["error"], "not_found")
        device = inspect_device("LT-318", "vpn")
        self.assertEqual(device["asset_id"], "LT-318")
        self.assertEqual(inspect_device("LT-999", "all")["error"], "asset_not_found")
        self.assertEqual(lookup_user("EMP-1007")["employee"]["employee_id"], "EMP-1007")
        self.assertEqual(lookup_user("EMP-9999")["error"], "employee_not_found")
        self.assertTrue(search_kb("VPN macOS certificate", "vpn", 2)["results"])
        self.assertTrue(search_company_policy("external tool", "external_tools", 2)["results"])
        report = format_incident_report([{"label": "VPN", "detail": "degraded"}], "brief", "VPN incident")
        self.assertEqual(report["finding_count"], 1)
        self.assertIn("VPN incident", report["markdown"])

    def test_schema_constraints_are_not_runtime_validation(self) -> None:
        self.assertTrue(ask_user()["awaiting_user"])
        self.assertEqual(search_kb()["results"], [])
        self.assertEqual(check_service_status()["error"], "not_found")
        self.assertEqual(inspect_device()["error"], "asset_not_found")
        self.assertEqual(lookup_user()["error"], "employee_not_found")
        self.assertEqual(search_device_info()["error"], "missing_public_product_identity")
        self.assertEqual(create_ticket()["error"], "missing_summary")
        self.assertEqual(create_ticket("VPN", "not-an-enum", "", False)["error"], "invalid_priority")
        self.assertEqual(search_device_info("Lenovo", "T14", "not-an-enum")["error"], "invalid_query_type")
        self.assertEqual(check_service_status("vpn", "not-an-enum")["error"], "not_found")
        self.assertEqual(inspect_device("LT-318", "not-an-enum")["check"], "not-an-enum")
        self.assertEqual(search_kb("VPN", "not-an-enum", 1)["category"], "not-an-enum")
        self.assertEqual(format_incident_report([], "not-an-enum", "title")["template"], "not-an-enum")

    def test_search_device_info_rejects_internal_values_before_network(self) -> None:
        blocked_values = [
            ("Lenovo", "serial number=SN-12345"),
            ("Dell", "hostname=ws-17.corp"),
            ("HP", "location=Hanoi office"),
            ("Lenovo", "192.168.10.4"),
            ("Dell", "diagnostic=VPN failure"),
            ("HP", "token=not-real"),
        ]
        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-only"}, clear=False), patch(
            "tools.search_device_info.tool.requests.post"
        ) as post:
            for manufacturer, model in blocked_values:
                result = search_device_info(manufacturer, model, "support", 2)
                self.assertEqual(result["error"], "restricted_internal_data")
            post.assert_not_called()

    def test_search_device_info_missing_key_does_not_call_network(self) -> None:
        with patch.dict("os.environ", {}, clear=True), patch(
            "tools.search_device_info.tool.requests.post"
        ) as post:
            result = search_device_info("Lenovo", "ThinkPad T14 Gen 4", "support", 2)
        self.assertEqual(result["error"], "missing_api_key")
        post.assert_not_called()

    def test_search_device_info_sends_only_public_query_and_handles_empty_result(self) -> None:
        response = Mock()
        response.json.return_value = {"results": []}
        response.raise_for_status.return_value = None
        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-only"}, clear=False), patch(
            "tools.search_device_info.tool.requests.post", return_value=response
        ) as post:
            result = search_device_info("Lenovo", "ThinkPad T14 Gen 4", "drivers", 2)
        self.assertEqual(result["items"], [])
        request_body = post.call_args.kwargs["json"]
        self.assertIn("Lenovo ThinkPad T14 Gen 4 drivers and downloads official", request_body["query"])
        self.assertEqual(request_body["max_results"], 2)
        self.assertNotIn("TAVILY_API_KEY", request_body["query"])

    def test_search_device_info_returns_api_error_without_faking_success(self) -> None:
        response = Mock()
        response.raise_for_status.side_effect = RuntimeError("mock Tavily failure")
        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-only"}, clear=False), patch(
            "tools.search_device_info.tool.requests.post", return_value=response
        ):
            result = search_device_info("Dell", "Latitude 5440", "support", 1)
        self.assertEqual(result["error"], "RuntimeError")

    def test_create_ticket_requires_real_boolean_and_rejects_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "tools.create_ticket.tool.TICKET_DIR", Path(temp_dir)
        ):
            for forged_confirmation in ("true", 1, {"confirmed": True}):
                result = create_ticket("VPN issue", "low", "LT-204", forged_confirmation)
                self.assertEqual(result["status"], "needs_confirmation")
            result = create_ticket("VPN token: not-real", "low", "LT-204", True)
            self.assertEqual(result["error"], "restricted_sensitive_data")
            self.assertEqual(list(Path(temp_dir).iterdir()), [])

            created = create_ticket("VPN unavailable", "high", "LT-204", True)
            self.assertEqual(created["status"], "created")
            ticket_path = Path(created["path"])
            self.assertTrue(ticket_path.exists())
            ticket_text = ticket_path.read_text(encoding="utf-8")
            self.assertIn("VPN unavailable", ticket_text)
            self.assertNotIn("password", ticket_text.casefold())


if __name__ == "__main__":
    unittest.main()
