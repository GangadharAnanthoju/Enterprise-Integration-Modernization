from tools.contracts import RiskLevel
from tools.registry import get_tool, list_tools, require_tool


EXPECTED_TOOL_NAMES = {
    "getOrderStatus",
    "validateInvoice",
    "checkShipmentStatus",
    "sendSupplierNotification",
    "createApprovalRequest",
    "createServiceNowTicket",
    "queryIntegrationRunStatus",
}


def test_registry_contains_expected_enterprise_mcp_tools() -> None:
    tool_names = {tool.name for tool in list_tools()}

    assert tool_names == EXPECTED_TOOL_NAMES


def test_high_risk_tools_require_approval() -> None:
    high_risk_tools = [tool for tool in list_tools() if tool.risk_level == RiskLevel.HIGH]

    assert high_risk_tools
    assert all(tool.approval_required for tool in high_risk_tools)


def test_read_only_lookup_tools_are_low_risk() -> None:
    assert require_tool("getOrderStatus").risk_level == RiskLevel.LOW
    assert require_tool("checkShipmentStatus").risk_level == RiskLevel.LOW
    assert require_tool("queryIntegrationRunStatus").risk_level == RiskLevel.LOW


def test_tool_contracts_include_required_entities() -> None:
    assert require_tool("getOrderStatus").required_entities == ("order_id",)
    assert require_tool("validateInvoice").required_entities == ("invoice_id",)
    assert require_tool("checkShipmentStatus").required_entities == ("shipment_id",)
    assert require_tool("sendSupplierNotification").required_entities == ("shipment_id",)
    assert require_tool("queryIntegrationRunStatus").required_entities == ("correlation_id",)


def test_unknown_tool_returns_none_or_clear_error() -> None:
    assert get_tool("deletePurchaseOrder") is None

    try:
        require_tool("deletePurchaseOrder")
    except KeyError as exc:
        assert "Unsupported MCP tool" in str(exc)
    else:
        raise AssertionError("Unsupported tools must not be returned from the registry.")
