"""Tests for the read-only MCP tool layer (mcp/server.py + mcp/tools)."""
from __future__ import annotations

import json

from mcp import server
from mcp.tools import call_tool, list_tools

EXPECTED_TOOLS = {
    "recent_deployments",
    "service_context",
    "similar_incidents",
    "escalation_preview",
}


def test_list_tools_exposes_four_piter_tools():
    names = {t["name"] for t in list_tools()}
    assert names == EXPECTED_TOOLS
    for tool in list_tools():
        assert tool["description"]
        assert tool["inputSchema"]["type"] == "object"


def test_initialize_handshake():
    resp = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["result"]["serverInfo"]["name"] == "piter-aiops"
    assert resp["result"]["protocolVersion"]


def test_initialized_notification_has_no_response():
    assert server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_tools_call_service_context_returns_owner():
    out = call_tool(
        "service_context",
        {"service": "postgres", "severity": "P2", "environment": "NJ-DGE"},
    )
    assert "owner" in out


def test_escalation_preview_never_sends_and_masks_recipient():
    out = call_tool("escalation_preview", {"service": "postgres", "severity": "P1"})
    assert out["mode"] == "preview"
    assert out["sends_notifications"] is False
    # masked recipient must not equal a full raw value
    assert "***" in out["recipient_masked"] or out["recipient_masked"] == ""


def test_tools_call_via_protocol_returns_text_content():
    resp = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "similar_incidents",
                "arguments": {"service": "postgres", "symptom": "CPU above 90%"},
            },
        }
    )
    assert resp["result"]["isError"] is False
    body = json.loads(resp["result"]["content"][0]["text"])
    assert "similar_incidents" in body or "service" in body


def test_unknown_tool_returns_method_not_found_error():
    resp = server.handle(
        {"jsonrpc": "2.0", "id": 10, "method": "tools/call", "params": {"name": "nope", "arguments": {}}}
    )
    assert resp["error"]["code"] == -32601
