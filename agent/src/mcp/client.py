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

    response_path = _repo_root() / tool.output_schema_ref
    with response_path.open(encoding="utf-8") as response_file:
        return json.load(response_file)


def simulate_mcp_tool(
    tool: ToolContract,
    risk_decision: RiskDecision,
    correlation_id: str,
) -> McpSimulationResult:
    """Simulate an MCP tool call without connecting to Azure."""

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
