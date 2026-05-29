from foundry.tool_registration import (
    list_foundry_tool_registrations,
    validate_foundry_tool_registrations,
)


def test_foundry_tool_registration_metadata_matches_approved_registry() -> None:
    registrations = list_foundry_tool_registrations()

    assert {registration.name for registration in registrations} == {
        "getOrderStatus",
        "checkShipmentStatus",
        "validateInvoice",
        "queryIntegrationRunStatus",
        "createApprovalRequest",
        "sendSupplierNotification",
        "createServiceNowTicket",
    }
    assert validate_foundry_tool_registrations() == []


def test_foundry_tool_registration_keeps_high_risk_approval_metadata() -> None:
    registrations = {
        registration.name: registration for registration in list_foundry_tool_registrations()
    }

    assert registrations["sendSupplierNotification"].risk_level == "high"
    assert registrations["sendSupplierNotification"].approval_required is True
    assert registrations["createServiceNowTicket"].risk_level == "high"
    assert registrations["createServiceNowTicket"].approval_required is True


def test_foundry_tool_registration_includes_endpoint_settings() -> None:
    registrations = {
        registration.name: registration for registration in list_foundry_tool_registrations()
    }

    assert (
        registrations["getOrderStatus"].endpoint_setting
        == "MCP_TOOL_ENDPOINT_GET_ORDER_STATUS"
    )
    assert (
        registrations["sendSupplierNotification"].endpoint_setting
        == "MCP_TOOL_ENDPOINT_SEND_SUPPLIER_NOTIFICATION"
    )
    assert all(
        registration.execution_boundary == "MCP"
        for registration in registrations.values()
    )
