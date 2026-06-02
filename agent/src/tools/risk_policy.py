"""Risk policy for approved enterprise MCP tool execution."""

from dataclasses import dataclass
from enum import StrEnum

from tools.contracts import RiskLevel, ToolContract
from tools.registry import require_tool


class ExecutionDecision(StrEnum):
    """Decision returned before an MCP tool can run."""

    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class RiskDecision:
    """Result of evaluating one MCP tool against enterprise risk policy."""

    tool_name: str
    risk_level: RiskLevel
    decision: ExecutionDecision
    approval_required: bool
    audit_required: bool
    reason: str


def evaluate_tool_risk(tool: ToolContract) -> RiskDecision:
    """Evaluate whether a registered MCP tool can execute immediately."""

    # High-risk tools may create external or operational impact, so they stop
    # here until a human approval flow is completed.
    if tool.risk_level == RiskLevel.HIGH or tool.approval_required:
        return RiskDecision(
            tool_name=tool.name,
            risk_level=tool.risk_level,
            decision=ExecutionDecision.REQUIRE_APPROVAL,
            approval_required=True,
            audit_required=True,
            reason="High-risk enterprise actions require human approval before execution.",
        )

    # Medium-risk tools can run, but we still require audit logging so the
    # enterprise can explain what happened later.
    if tool.risk_level == RiskLevel.MEDIUM:
        return RiskDecision(
            tool_name=tool.name,
            risk_level=tool.risk_level,
            decision=ExecutionDecision.ALLOW,
            approval_required=False,
            audit_required=True,
            reason="Medium-risk tools can execute with audit logging.",
        )

    # Low-risk tools are normally read-only lookups. They can run immediately,
    # but we still audit them for traceability.
    return RiskDecision(
        tool_name=tool.name,
        risk_level=tool.risk_level,
        decision=ExecutionDecision.ALLOW,
        approval_required=False,
        audit_required=True,
        reason="Low-risk read-only tools can execute with standard audit logging.",
    )


def evaluate_tool_name(tool_name: str) -> RiskDecision:
    """Evaluate a tool by registered MCP tool name."""

    return evaluate_tool_risk(require_tool(tool_name))
