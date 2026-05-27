"""FastAPI routes for catalog and agent operations."""

from fastapi import APIRouter, Body, HTTPException

from agent_app import AgentChatResult, handle_chat_message
from api.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    RiskDecisionResponse,
    ToolResponse,
    ToolSimulationRequest,
    ToolSimulationResponse,
)
from mcp.client import McpSimulationResult, simulate_mcp_tool
from telemetry.correlation import resolve_correlation_id
from tools.contracts import ToolContract
from tools.registry import get_tool, list_tools
from tools.risk_policy import RiskDecision, evaluate_tool_risk

router = APIRouter()


def _to_agent_chat_response(result: AgentChatResult) -> AgentChatResponse:
    """Convert the agent shell result into the public API response shape."""

    return AgentChatResponse(
        correlation_id=result.correlation_id,
        status=result.status,
        message=result.message,
        tool_called=result.tool_called,
    )


def _to_tool_response(tool: ToolContract) -> ToolResponse:
    """Convert internal tool metadata into the public API response shape."""

    # Keep this mapping explicit so the API response is stable even if the
    # internal ToolContract changes later.
    return ToolResponse(
        name=tool.name,
        description=tool.description,
        business_domain=tool.business_domain,
        backend_system=tool.backend_system,
        risk_level=tool.risk_level.value,
        approval_required=tool.approval_required,
        owner=tool.owner,
        version=tool.version,
        operational_impact=tool.operational_impact,
        input_schema_ref=tool.input_schema_ref,
        output_schema_ref=tool.output_schema_ref,
    )


def _to_risk_decision_response(decision: RiskDecision) -> RiskDecisionResponse:
    """Convert an internal risk decision into the public API response shape."""

    return RiskDecisionResponse(
        tool_name=decision.tool_name,
        risk_level=decision.risk_level.value,
        decision=decision.decision.value,
        approval_required=decision.approval_required,
        audit_required=decision.audit_required,
        reason=decision.reason,
    )


def _to_simulation_response(result: McpSimulationResult) -> ToolSimulationResponse:
    """Convert a mock MCP result into the public API response shape."""

    return ToolSimulationResponse(
        tool_name=result.tool_name,
        correlation_id=result.correlation_id,
        mode=result.mode,
        status=result.status,
        risk_decision=result.risk_decision,
        approval_required=result.approval_required,
        result=result.result,
        message=result.message,
    )


@router.get("/tools", response_model=list[ToolResponse])
async def get_tools() -> list[ToolResponse]:
    """Return the approved enterprise MCP tool catalog."""

    # This endpoint is like a read-only tool catalog page for clients.
    return [_to_tool_response(tool) for tool in list_tools()]


@router.post("/agent/chat", response_model=AgentChatResponse)
async def chat_with_agent(request: AgentChatRequest) -> AgentChatResponse:
    """Accept a user message through the safe agent shell."""

    correlation_id = resolve_correlation_id(request.correlation_id)
    result = handle_chat_message(request.user_message, correlation_id)
    return _to_agent_chat_response(result)


@router.get("/tools/{tool_name}", response_model=ToolResponse)
async def get_tool_by_name(tool_name: str) -> ToolResponse:
    """Return metadata for one approved MCP tool."""

    tool = get_tool(tool_name)
    if tool is None:
        # Unknown tools must fail clearly. The agent should never invent or run
        # unsupported enterprise actions.
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")

    return _to_tool_response(tool)


@router.get("/tools/{tool_name}/risk", response_model=RiskDecisionResponse)
async def get_tool_risk(tool_name: str) -> RiskDecisionResponse:
    """Return the pre-execution risk decision for one approved MCP tool."""

    tool = get_tool(tool_name)
    if tool is None:
        # Risk policy only applies to approved tools in the registry.
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")

    return _to_risk_decision_response(evaluate_tool_risk(tool))


@router.post("/tools/{tool_name}/simulate", response_model=ToolSimulationResponse)
async def simulate_tool(
    tool_name: str,
    request: ToolSimulationRequest | None = Body(default=None),
) -> ToolSimulationResponse:
    """Simulate one approved MCP tool using local sample data."""

    tool = get_tool(tool_name)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")

    correlation_id = resolve_correlation_id(request.correlation_id if request else None)
    risk_decision = evaluate_tool_risk(tool)
    return _to_simulation_response(simulate_mcp_tool(tool, risk_decision, correlation_id))
