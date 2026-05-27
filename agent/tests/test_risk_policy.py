from tools.contracts import RiskLevel
from tools.risk_policy import ExecutionDecision, evaluate_tool_name


def test_low_risk_tools_are_allowed_with_audit() -> None:
    decision = evaluate_tool_name("getOrderStatus")

    assert decision.risk_level == RiskLevel.LOW
    assert decision.decision == ExecutionDecision.ALLOW
    assert decision.approval_required is False
    assert decision.audit_required is True


def test_medium_risk_tools_are_allowed_with_audit() -> None:
    decision = evaluate_tool_name("validateInvoice")

    assert decision.risk_level == RiskLevel.MEDIUM
    assert decision.decision == ExecutionDecision.ALLOW
    assert decision.approval_required is False
    assert decision.audit_required is True


def test_high_risk_supplier_notification_requires_approval() -> None:
    decision = evaluate_tool_name("sendSupplierNotification")

    assert decision.risk_level == RiskLevel.HIGH
    assert decision.decision == ExecutionDecision.REQUIRE_APPROVAL
    assert decision.approval_required is True
    assert decision.audit_required is True


def test_high_risk_servicenow_ticket_requires_approval() -> None:
    decision = evaluate_tool_name("createServiceNowTicket")

    assert decision.risk_level == RiskLevel.HIGH
    assert decision.decision == ExecutionDecision.REQUIRE_APPROVAL
    assert decision.approval_required is True
    assert decision.audit_required is True


def test_unknown_tool_is_rejected_before_policy_decision() -> None:
    try:
        evaluate_tool_name("deletePurchaseOrder")
    except KeyError as exc:
        assert "Unsupported MCP tool" in str(exc)
    else:
        raise AssertionError("Unknown tools must not receive an execution decision.")
