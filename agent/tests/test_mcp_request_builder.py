import pytest

from config import Settings
from mcp.client import (
    build_mcp_request,
    load_mcp_config,
    simulate_mcp_tool,
    simulate_mcp_tool_after_approval,
)
from mcp.exceptions import MissingRequiredEntitiesError
from mcp.schemas import McpExecutionMode
from tools.registry import require_tool
from tools.risk_policy import evaluate_tool_risk


def test_build_mcp_request_uses_required_entity_payload() -> None:
    tool = require_tool("getOrderStatus")

    request = build_mcp_request(
        tool=tool,
        entities={"order_id": "ORD-1001", "shipment_id": "SHIP-ignored"},
        correlation_id="chat-corr-001",
    )

    assert request.tool_name == "getOrderStatus"
    assert request.correlation_id == "chat-corr-001"
    assert request.payload == {"order_id": "ORD-1001"}


def test_build_mcp_request_allows_tools_without_required_entities() -> None:
    tool = require_tool("createApprovalRequest")

    request = build_mcp_request(
        tool=tool,
        entities={},
        correlation_id="chat-corr-002",
    )

    assert request.tool_name == "createApprovalRequest"
    assert request.payload == {}


def test_build_mcp_request_reports_missing_required_entities() -> None:
    tool = require_tool("sendSupplierNotification")

    with pytest.raises(MissingRequiredEntitiesError) as exc_info:
        build_mcp_request(
            tool=tool,
            entities={},
            correlation_id="chat-corr-003",
        )

    assert exc_info.value.tool_name == "sendSupplierNotification"
    assert exc_info.value.missing_entities == ["shipment_id"]


def test_simulate_mcp_tool_includes_validated_request_payload() -> None:
    tool = require_tool("getOrderStatus")

    result = simulate_mcp_tool(
        tool=tool,
        risk_decision=evaluate_tool_risk(tool),
        correlation_id="chat-corr-004",
        entities={"order_id": "ORD-1001"},
    )

    assert result.status == "completed"
    assert result.request is not None
    assert result.request.payload == {"order_id": "ORD-1001"}
    assert result.result["orderNumber"] == "4500098123"


def test_simulate_mcp_tool_after_approval_includes_validated_request_payload() -> None:
    tool = require_tool("sendSupplierNotification")

    result = simulate_mcp_tool_after_approval(
        tool=tool,
        risk_decision=evaluate_tool_risk(tool),
        correlation_id="chat-corr-005",
        approval_id="apr-chat-corr-005",
        entities={"shipment_id": "SHIP-3001"},
    )

    assert result.status == "completed"
    assert result.request is not None
    assert result.request.payload == {"shipment_id": "SHIP-3001"}


def test_load_mcp_config_defaults_to_mock_mode() -> None:
    config = load_mcp_config(Settings())

    assert config.mode == McpExecutionMode.MOCK
    assert config.server_name == "logic-apps-standard-mcp"
    assert config.endpoint_url is None
    assert config.endpoint_configured is False
    assert config.timeout_seconds == 30


def test_load_mcp_config_supports_remote_mode() -> None:
    config = load_mcp_config(
        Settings(
            mock_mcp=False,
            mcp_execution_mode="remote",
            mcp_server_name="logic-apps-prod-mcp",
            mcp_server_url="https://example.contoso/mcp",
            mcp_timeout_seconds=45,
        )
    )

    assert config.mode == McpExecutionMode.REMOTE
    assert config.server_name == "logic-apps-prod-mcp"
    assert config.endpoint_url == "https://example.contoso/mcp"
    assert config.endpoint_configured is True
    assert config.timeout_seconds == 45
