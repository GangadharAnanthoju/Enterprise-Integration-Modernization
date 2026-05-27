from typing import Any

from pydantic import BaseModel


class ToolSimulationRequest(BaseModel):
    """Optional request body for local mock MCP tool simulation."""

    # In real integrations, callers often pass an existing correlation ID.
    # If omitted, the API generates one for the simulation.
    correlation_id: str | None = None


class AgentChatRequest(BaseModel):
    """Request body for the agent chat endpoint."""

    # This is the user's natural-language request.
    user_message: str
    correlation_id: str | None = None


class AgentChatResponse(BaseModel):
    """Response body for the safe agent chat placeholder."""

    correlation_id: str
    status: str
    message: str
    tool_called: bool


class ToolResponse(BaseModel):
    """Public API shape for one approved MCP tool."""

    # These fields are what callers see when they query /tools.
    # They intentionally include governance metadata, not only technical names.
    name: str
    description: str
    business_domain: str
    backend_system: str
    risk_level: str
    approval_required: bool
    owner: str
    version: str
    operational_impact: str
    input_schema_ref: str
    output_schema_ref: str


class RiskDecisionResponse(BaseModel):
    """Public API shape for the pre-execution risk decision."""

    # This tells a caller whether the selected MCP tool can run immediately
    # or must wait for human approval.
    tool_name: str
    risk_level: str
    decision: str
    approval_required: bool
    audit_required: bool
    reason: str


class ToolSimulationResponse(BaseModel):
    """Public API shape for local mock MCP tool simulation."""

    # In mock mode, low/medium-risk tools return sample data.
    # High-risk tools return approval_required instead of pretending execution happened.
    tool_name: str
    correlation_id: str
    mode: str
    status: str
    risk_decision: str
    approval_required: bool
    result: dict[str, Any] | None
    message: str
