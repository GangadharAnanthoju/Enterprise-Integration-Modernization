"""Shared governed execution flow for local and Foundry agent plans."""

from agent_contracts import AgentChatResult, PlannedAction
from approvals.requests import create_approval_request
from mcp.client import simulate_mcp_tool
from tools.registry import get_tool
from tools.risk_policy import ExecutionDecision, evaluate_tool_risk


def get_missing_entities(tool_name: str, entities: dict[str, str]) -> list[str]:
    """Return required entity names that are missing for a selected tool."""

    tool = get_tool(tool_name)
    if tool is None:
        return []

    return [entity_name for entity_name in tool.required_entities if entity_name not in entities]


def execute_planned_action(
    *,
    selected_tool: str,
    entities: dict[str, str],
    correlation_id: str,
    simulate_when_ready: bool = False,
    missing_entities: list[str] | None = None,
    plan_only_message: str | None = None,
    missing_entities_message: str | None = None,
    unsupported_tool_message: str | None = None,
) -> AgentChatResult:
    """Apply governance and optional MCP execution to a selected approved tool."""

    tool = get_tool(selected_tool)
    if tool is None:
        return AgentChatResult(
            correlation_id=correlation_id,
            status="unsupported_tool",
            message=unsupported_tool_message
            or f"The selected tool '{selected_tool}' is not in the approved catalog.",
            tool_called=False,
            selected_tool=selected_tool,
            risk_decision=None,
            approval_required=None,
            entities=entities,
            planned_action=None,
            simulation_result=None,
            approval_request=None,
        )

    risk_decision = evaluate_tool_risk(tool)
    resolved_missing_entities = (
        missing_entities
        if missing_entities is not None
        else get_missing_entities(tool.name, entities)
    )
    planned_action = PlannedAction(
        tool_name=tool.name,
        entities=entities,
        risk_decision=risk_decision.decision.value,
        approval_required=risk_decision.approval_required,
        ready_for_simulation=not resolved_missing_entities,
        missing_entities=resolved_missing_entities,
    )
    if not simulate_when_ready:
        return AgentChatResult(
            correlation_id=correlation_id,
            status="tool_selected",
            message=plan_only_message
            or (
                f"Agent selected approved tool '{tool.name}'. Execution is not automatic yet; "
                "set simulate_when_ready=true to test MCP execution from chat."
            ),
            tool_called=False,
            selected_tool=tool.name,
            risk_decision=risk_decision.decision.value,
            approval_required=risk_decision.approval_required,
            entities=entities,
            planned_action=planned_action,
            simulation_result=None,
            approval_request=None,
        )

    if resolved_missing_entities:
        return AgentChatResult(
            correlation_id=correlation_id,
            status="missing_required_entities",
            message=missing_entities_message
            or (
                f"Agent selected approved tool '{tool.name}', but MCP execution "
                f"needs: {', '.join(resolved_missing_entities)}."
            ),
            tool_called=False,
            selected_tool=tool.name,
            risk_decision=risk_decision.decision.value,
            approval_required=risk_decision.approval_required,
            entities=entities,
            planned_action=planned_action,
            simulation_result=None,
            approval_request=None,
        )

    if risk_decision.decision != ExecutionDecision.ALLOW:
        approval_request = create_approval_request(
            correlation_id=correlation_id,
            requested_tool=tool.name,
            requested_entities=entities,
            reason=risk_decision.reason,
        )
        return AgentChatResult(
            correlation_id=correlation_id,
            status="approval_required",
            message=(
                f"Agent selected approved tool '{tool.name}', but this action requires "
                "human approval before MCP execution. A pending approval request was created."
            ),
            tool_called=False,
            selected_tool=tool.name,
            risk_decision=risk_decision.decision.value,
            approval_required=risk_decision.approval_required,
            entities=entities,
            planned_action=planned_action,
            simulation_result=None,
            approval_request=approval_request,
        )

    simulation_result = simulate_mcp_tool(tool, risk_decision, correlation_id, entities)
    return AgentChatResult(
        correlation_id=correlation_id,
        status=simulation_result.status,
        message=f"Agent selected approved tool '{tool.name}' and completed MCP execution.",
        tool_called=True,
        selected_tool=tool.name,
        risk_decision=risk_decision.decision.value,
        approval_required=risk_decision.approval_required,
        entities=entities,
        planned_action=planned_action,
        simulation_result=simulation_result,
        approval_request=None,
    )
