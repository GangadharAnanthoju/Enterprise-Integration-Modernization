from typing import Any, Literal

from pydantic import BaseModel


# **************** KEEP: PUBLIC API CONTRACTS ****************
# These Pydantic classes are the frontend/API boundary. Even after the real
# Foundry agent is implemented, keep these response shapes stable unless we
# intentionally version the API.
# ************************************************************


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
    # False means planning only. True lets chat run the mock MCP path when the
    # planned action is complete and risk policy allows it.
    simulate_when_ready: bool = False


class PlannedActionResponse(BaseModel):
    """Structured action plan returned before tool execution."""

    # KEEP: This is the public version of the internal PlannedAction. The real
    # agent should still return this planning shape before execution.
    tool_name: str
    entities: dict[str, str]
    risk_decision: str
    approval_required: bool
    ready_for_simulation: bool
    missing_entities: list[str]


class ToolSimulationResponse(BaseModel):
    """Public API shape for local mock MCP tool simulation."""

    # TEMPORARY RESULT SOURCE: this response currently comes from mock MCP
    # simulation. Later it can come from the real MCP server with the same API
    # shape.
    # In mock mode, low/medium-risk tools return sample data.
    # High-risk tools return approval_required instead of pretending execution happened.
    tool_name: str
    correlation_id: str
    mode: str
    status: str
    risk_decision: str
    approval_required: bool
    request_payload: dict[str, Any] | None = None
    result: dict[str, Any] | None
    message: str


class McpServerConfigResponse(BaseModel):
    """Public API shape for MCP server runtime configuration."""

    mode: str
    server_name: str
    endpoint_configured: bool
    api_key_configured: bool
    timeout_seconds: int


class McpExecutorDiagnosticsResponse(BaseModel):
    """Public API shape for active MCP executor diagnostics."""

    mode: str
    executor_name: str
    server_name: str
    endpoint_configured: bool
    remote_transport: str


class AgentAdapterResponse(BaseModel):
    """Public API shape for the active agent runtime adapter."""

    name: str
    runtime: str
    implementation_status: str


class ApprovalRequestResponse(BaseModel):
    """Public API shape for a pending high-risk action approval."""

    # TEMPORARY STORAGE: approval requests are currently in-memory. The API
    # shape can stay the same when approvals move to a workflow or database.
    # This is returned instead of a simulation result when a ready action is
    # blocked by high-risk policy.
    approval_id: str
    correlation_id: str
    requested_tool: str
    requested_entities: dict[str, str]
    status: str
    reason: str


class ApprovalDecisionRequest(BaseModel):
    """Request body for approving or rejecting a pending approval."""

    decision: Literal["approved", "rejected"]
    reviewer: str
    comment: str | None = None


class ApprovalDecisionResponse(BaseModel):
    """Public API shape for a recorded approval decision."""

    approval_id: str
    correlation_id: str
    requested_tool: str
    decision: str
    status: str
    reviewer: str
    comment: str | None


class ApprovalExecutionResponse(BaseModel):
    """Public API shape for executing an approved high-risk action."""

    approval_id: str
    approval_status: str
    execution_status: str
    tool_name: str
    correlation_id: str
    simulation_result: ToolSimulationResponse
    message: str


class AuditEventResponse(BaseModel):
    """Public API shape for one audit event."""

    event_id: str
    correlation_id: str
    event_type: str
    source: str
    status: str
    details: dict[str, Any]


class FoundryTraceResponse(BaseModel):
    """Public API shape for a Foundry-style trace record."""

    trace_id: str
    correlation_id: str
    span_name: str
    span_kind: str
    status: str
    source: str
    attributes: dict[str, Any]


class AppInsightsEventResponse(BaseModel):
    """Public API shape for an Application Insights custom event envelope."""

    name: str
    operation_id: str
    severity: str
    properties: dict[str, Any]


class EvaluationExpectedOutcomeResponse(BaseModel):
    """Public API shape for an evaluation case expected outcome."""

    status: str
    selected_tool: str | None
    ready_for_simulation: bool | None
    missing_entities: list[str] | None
    approval_required: bool | None
    tool_called: bool
    approval_request_created: bool


class EvaluationCaseResponse(BaseModel):
    """Public API shape for one local Foundry-style evaluation case."""

    case_id: str
    user_message: str
    simulate_when_ready: bool
    expected: EvaluationExpectedOutcomeResponse
    expected_behavior: str


class EvaluationResultResponse(BaseModel):
    """Public API shape for one local evaluation result."""

    case_id: str
    passed: bool
    expected_behavior: str
    actual_status: str
    actual_selected_tool: str | None
    actual_tool_called: bool
    failures: list[str]


class ReadinessCheckResponse(BaseModel):
    """Public API shape for one operational readiness check."""

    name: str
    status: str
    details: str


class ReadinessReportResponse(BaseModel):
    """Public API shape for operational readiness."""

    status: str
    checks: list[ReadinessCheckResponse]


class AgentChatResponse(BaseModel):
    """Response body for the safe agent chat placeholder."""

    # KEEP: This is the main future frontend response. It supports all current
    # branches: plan only, completed simulation, missing data, or approval.
    correlation_id: str
    status: str
    message: str
    tool_called: bool
    selected_tool: str | None
    risk_decision: str | None
    approval_required: bool | None
    entities: dict[str, str]
    # The plan is present after tool selection, even when execution is blocked.
    planned_action: PlannedActionResponse | None
    # Populated only when chat was explicitly allowed to simulate and policy
    # permitted the selected tool.
    simulation_result: ToolSimulationResponse | None = None
    # Populated only when a ready high-risk action needs human review.
    approval_request: ApprovalRequestResponse | None = None


class ToolResponse(BaseModel):
    """Public API shape for one approved MCP tool."""

    # KEEP: This exposes the governed tool catalog. The backend source may
    # later move from static Python to a registry service or config store.
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
    required_entities: list[str]
    input_schema_ref: str
    output_schema_ref: str


class RiskDecisionResponse(BaseModel):
    """Public API shape for the pre-execution risk decision."""

    # KEEP: Risk decisions should remain visible to callers for governance,
    # troubleshooting, and interview-friendly explainability.
    # This tells a caller whether the selected MCP tool can run immediately
    # or must wait for human approval.
    tool_name: str
    risk_level: str
    decision: str
    approval_required: bool
    audit_required: bool
    reason: str
