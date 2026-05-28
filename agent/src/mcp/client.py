"""MCP client adapter.

For now this module supports local mock execution. Later, the same boundary
will call the remote Logic Apps Standard MCP server.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.contracts import ToolContract
from tools.risk_policy import ExecutionDecision, RiskDecision


# **************** TEMPORARY MOCK MCP ADAPTER ****************
# This module is active now for local simulation. After the real enterprise MCP
# server exists, replace sample-file loading with remote MCP tool calls while
# keeping risk checks and correlation IDs.
# ************************************************************


@dataclass(frozen=True)
class McpSimulationResult:
    """Result returned by local mock MCP simulation."""

    tool_name: str
    correlation_id: str
    mode: str
    status: str
    risk_decision: str
    approval_required: bool
    result: dict[str, Any] | None
    message: str


def _repo_root() -> Path:
    """Return the repository root from this source file location."""

    return Path(__file__).resolve().parents[3]


def _load_sample_response(tool: ToolContract) -> dict[str, Any]:
    """Load the sample Logic Apps response for a tool."""

    # TEMPORARY SAMPLE DATA: this stands in for Logic Apps/MCP output while the
    # project proves contracts and governance locally.
    response_path = _repo_root() / tool.output_schema_ref
    with response_path.open(encoding="utf-8") as response_file:
        return json.load(response_file)


def simulate_mcp_tool(
    tool: ToolContract,
    risk_decision: RiskDecision,
    correlation_id: str,
) -> McpSimulationResult:
    """Simulate an MCP tool call without connecting to Azure."""

    # KEEP: high-risk tools must stop here too. Even direct simulation endpoint
    # calls should respect the same policy as the chat flow.
    if risk_decision.decision == ExecutionDecision.REQUIRE_APPROVAL:
        return McpSimulationResult(
            tool_name=tool.name,
            correlation_id=correlation_id,
            mode="mock",
            status="approval_required",
            risk_decision=risk_decision.decision.value,
            approval_required=True,
            result=None,
            message="Tool simulation stopped because this action requires approval.",
        )

    return McpSimulationResult(
        tool_name=tool.name,
        correlation_id=correlation_id,
        mode="mock",
        status="completed",
        risk_decision=risk_decision.decision.value,
        approval_required=False,
        result=_load_sample_response(tool),
        message="Tool simulation completed using the local sample response.",
    )


def simulate_mcp_tool_after_approval(
    tool: ToolContract,
    risk_decision: RiskDecision,
    correlation_id: str,
    approval_id: str,
) -> McpSimulationResult:
    """Simulate a high-risk MCP tool only after approval is recorded."""

    # EXPLICIT APPROVAL PATH: this is the only place high-risk tools can move
    # past require_approval in local simulation. Direct tool simulation remains
    # blocked by simulate_mcp_tool().
    return McpSimulationResult(
        tool_name=tool.name,
        correlation_id=correlation_id,
        mode="mock",
        status="completed",
        risk_decision=risk_decision.decision.value,
        approval_required=False,
        result=_load_sample_response(tool),
        message=f"Tool simulation completed after approval {approval_id}.",
    )
