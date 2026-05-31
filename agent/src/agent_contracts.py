"""Shared agent response contracts used by local and Foundry runtimes."""

from dataclasses import dataclass

from approvals.requests import ApprovalRequest
from mcp.client import McpSimulationResult


@dataclass(frozen=True)
class PlannedAction:
    """Structured plan created before any tool execution."""

    tool_name: str
    entities: dict[str, str]
    risk_decision: str
    approval_required: bool
    ready_for_simulation: bool
    missing_entities: list[str]


@dataclass(frozen=True)
class AgentChatResult:
    """Safe result returned by an agent runtime adapter."""

    correlation_id: str
    status: str
    message: str
    tool_called: bool
    selected_tool: str | None
    risk_decision: str | None
    approval_required: bool | None
    entities: dict[str, str]
    planned_action: PlannedAction | None
    simulation_result: McpSimulationResult | None
    approval_request: ApprovalRequest | None
