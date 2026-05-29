"""FastAPI routes for catalog and agent operations."""

from fastapi import APIRouter, Body, HTTPException

from approvals.requests import (
    ApprovalDecision,
    ApprovalRequest,
    decide_approval_request,
    get_approval_decision,
    get_approval_request,
)
from agent_app import AgentChatResult, PlannedAction
from api.schemas import (
    AgentAdapterResponse,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalExecutionResponse,
    ApprovalRequestResponse,
    AgentChatRequest,
    AgentChatResponse,
    AppInsightsEventResponse,
    AuditEventResponse,
    EvaluationCaseResponse,
    EvaluationExpectedOutcomeResponse,
    EvaluationResultResponse,
    FoundryTraceResponse,
    McpExecutorDiagnosticsResponse,
    McpServerConfigResponse,
    PlannedActionResponse,
    ReadinessCheckResponse,
    ReadinessReportResponse,
    RiskDecisionResponse,
    ToolResponse,
    ToolSimulationRequest,
    ToolSimulationResponse,
)
from audit.events import AuditEvent, list_audit_events, record_audit_event
from foundry.evaluations import (
    EvaluationCase,
    EvaluationExpectedOutcome,
    EvaluationResult,
    list_evaluation_cases,
    run_local_evaluation_suite,
)
from foundry.governance import ReadinessCheck, ReadinessReport, run_readiness_checks
from foundry.agent_adapter import AgentRuntimeAdapter, get_agent_adapter
from foundry.tracing import FoundryTraceRecord, audit_events_to_foundry_traces
from mcp.client import (
    McpSimulationResult,
    load_mcp_config,
    simulate_mcp_tool,
    simulate_mcp_tool_after_approval,
)
from mcp.executors import McpExecutorDiagnostics, get_mcp_executor_diagnostics
from mcp.schemas import McpServerConfig
from telemetry.correlation import resolve_correlation_id
from telemetry.appinsights import AppInsightsCustomEvent, traces_to_appinsights_events
from tools.contracts import ToolContract
from tools.registry import get_tool, list_tools
from tools.risk_policy import RiskDecision, evaluate_tool_risk

router = APIRouter()


# **************** KEEP: API MAPPING LAYER ****************
# These mapper functions protect the public API from internal class changes.
# Keep this pattern when Foundry, persistence, or real MCP calls are added.
# *********************************************************


def _to_approval_request_response(
    approval_request: ApprovalRequest | None,
) -> ApprovalRequestResponse | None:
    """Convert an internal approval request into the public API response shape."""

    # Keep approval workflow internals behind an API schema so the frontend sees
    # a stable contract even when approval storage changes later.
    if approval_request is None:
        return None

    return ApprovalRequestResponse(
        approval_id=approval_request.approval_id,
        correlation_id=approval_request.correlation_id,
        requested_tool=approval_request.requested_tool,
        requested_entities=approval_request.requested_entities,
        status=approval_request.status,
        reason=approval_request.reason,
    )


def _to_audit_event_response(event: AuditEvent) -> AuditEventResponse:
    """Convert an internal audit event into the public API response shape."""

    return AuditEventResponse(
        event_id=event.event_id,
        correlation_id=event.correlation_id,
        event_type=event.event_type,
        source=event.source,
        status=event.status,
        details=event.details,
    )


def _to_foundry_trace_response(trace: FoundryTraceRecord) -> FoundryTraceResponse:
    """Convert an internal Foundry trace record into the public API response shape."""

    return FoundryTraceResponse(
        trace_id=trace.trace_id,
        correlation_id=trace.correlation_id,
        span_name=trace.span_name,
        span_kind=trace.span_kind,
        status=trace.status,
        source=trace.source,
        attributes=trace.attributes,
    )


def _to_appinsights_event_response(event: AppInsightsCustomEvent) -> AppInsightsEventResponse:
    """Convert an App Insights event envelope into the public API response shape."""

    return AppInsightsEventResponse(
        name=event.name,
        operation_id=event.operation_id,
        severity=event.severity,
        properties=event.properties,
    )


def _to_evaluation_expected_response(
    expected: EvaluationExpectedOutcome,
) -> EvaluationExpectedOutcomeResponse:
    """Convert an internal expected evaluation outcome to the API shape."""

    return EvaluationExpectedOutcomeResponse(
        status=expected.status,
        selected_tool=expected.selected_tool,
        ready_for_simulation=expected.ready_for_simulation,
        missing_entities=expected.missing_entities,
        approval_required=expected.approval_required,
        tool_called=expected.tool_called,
        approval_request_created=expected.approval_request_created,
    )


def _to_evaluation_case_response(case: EvaluationCase) -> EvaluationCaseResponse:
    """Convert an internal evaluation case to the API shape."""

    return EvaluationCaseResponse(
        case_id=case.case_id,
        user_message=case.user_message,
        simulate_when_ready=case.simulate_when_ready,
        expected=_to_evaluation_expected_response(case.expected),
        expected_behavior=case.expected_behavior,
    )


def _to_evaluation_result_response(result: EvaluationResult) -> EvaluationResultResponse:
    """Convert an internal evaluation result to the API shape."""

    return EvaluationResultResponse(
        case_id=result.case_id,
        passed=result.passed,
        expected_behavior=result.expected_behavior,
        actual_status=result.actual_status,
        actual_selected_tool=result.actual_selected_tool,
        actual_tool_called=result.actual_tool_called,
        failures=result.failures,
    )


def _to_readiness_check_response(check: ReadinessCheck) -> ReadinessCheckResponse:
    """Convert an internal readiness check to the API shape."""

    return ReadinessCheckResponse(
        name=check.name,
        status=check.status,
        details=check.details,
    )


def _to_readiness_report_response(report: ReadinessReport) -> ReadinessReportResponse:
    """Convert an internal readiness report to the API shape."""

    return ReadinessReportResponse(
        status=report.status,
        checks=[_to_readiness_check_response(check) for check in report.checks],
    )


def _to_approval_decision_response(decision: ApprovalDecision) -> ApprovalDecisionResponse:
    """Convert an internal approval decision into the public API response shape."""

    return ApprovalDecisionResponse(
        approval_id=decision.approval_id,
        correlation_id=decision.correlation_id,
        requested_tool=decision.requested_tool,
        decision=decision.decision,
        status=decision.status,
        reviewer=decision.reviewer,
        comment=decision.comment,
    )


def _to_planned_action_response(action: PlannedAction | None) -> PlannedActionResponse | None:
    """Convert an internal planned action into the public API response shape."""

    if action is None:
        return None

    return PlannedActionResponse(
        tool_name=action.tool_name,
        entities=action.entities,
        risk_decision=action.risk_decision,
        approval_required=action.approval_required,
        ready_for_simulation=action.ready_for_simulation,
        missing_entities=action.missing_entities,
    )


def _to_agent_chat_response(result: AgentChatResult) -> AgentChatResponse:
    """Convert the agent shell result into the public API response shape."""

    # The chat response can contain a plan, a simulation result, or an approval
    # request. Only one execution path should be populated for a given call.
    return AgentChatResponse(
        correlation_id=result.correlation_id,
        status=result.status,
        message=result.message,
        tool_called=result.tool_called,
        selected_tool=result.selected_tool,
        risk_decision=result.risk_decision,
        approval_required=result.approval_required,
        entities=result.entities,
        planned_action=_to_planned_action_response(result.planned_action),
        simulation_result=(
            _to_simulation_response(result.simulation_result)
            if result.simulation_result is not None
            else None
        ),
        approval_request=_to_approval_request_response(result.approval_request),
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
        required_entities=list(tool.required_entities),
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

    # TEMPORARY INPUT SOURCE: McpSimulationResult currently comes from the local
    # mock adapter. Later this mapper can accept a real MCP result object.
    return ToolSimulationResponse(
        tool_name=result.tool_name,
        correlation_id=result.correlation_id,
        mode=result.mode,
        status=result.status,
        risk_decision=result.risk_decision,
        approval_required=result.approval_required,
        request_payload=result.request.payload if result.request else None,
        result=result.result,
        message=result.message,
    )


def _to_mcp_config_response(config: McpServerConfig) -> McpServerConfigResponse:
    """Convert internal MCP runtime config to the public API response shape."""

    return McpServerConfigResponse(
        mode=config.mode.value,
        server_name=config.server_name,
        endpoint_configured=config.endpoint_configured,
        timeout_seconds=config.timeout_seconds,
    )


def _to_mcp_executor_diagnostics_response(
    diagnostics: McpExecutorDiagnostics,
) -> McpExecutorDiagnosticsResponse:
    """Convert MCP executor diagnostics to the public API response shape."""

    return McpExecutorDiagnosticsResponse(
        mode=diagnostics.mode,
        executor_name=diagnostics.executor_name,
        server_name=diagnostics.server_name,
        endpoint_configured=diagnostics.endpoint_configured,
        remote_transport=diagnostics.remote_transport,
    )


def _to_agent_adapter_response(adapter: AgentRuntimeAdapter) -> AgentAdapterResponse:
    """Convert active agent adapter metadata to the public API response shape."""

    return AgentAdapterResponse(
        name=adapter.name,
        runtime=adapter.runtime,
        implementation_status=adapter.implementation_status,
    )


def _to_approval_execution_response(
    *,
    approval_id: str,
    approval_status: str,
    simulation_result: McpSimulationResult,
) -> ApprovalExecutionResponse:
    """Convert approved high-risk execution into the public API response shape."""

    return ApprovalExecutionResponse(
        approval_id=approval_id,
        approval_status=approval_status,
        execution_status=simulation_result.status,
        tool_name=simulation_result.tool_name,
        correlation_id=simulation_result.correlation_id,
        simulation_result=_to_simulation_response(simulation_result),
        message=simulation_result.message,
    )


def _audit_chat_result(result: AgentChatResult) -> None:
    """Record audit events created by the chat planning flow."""

    record_audit_event(
        correlation_id=result.correlation_id,
        event_type="agent_chat_planned",
        source="agent.chat",
        status=result.status,
        details={
            "selected_tool": result.selected_tool,
            "risk_decision": result.risk_decision,
            "approval_required": result.approval_required,
            "tool_called": result.tool_called,
            "entities": result.entities,
        },
    )
    if result.approval_request is not None:
        record_audit_event(
            correlation_id=result.correlation_id,
            event_type="approval_request_created",
            source="agent.chat",
            status=result.approval_request.status,
            details={
                "approval_id": result.approval_request.approval_id,
                "requested_tool": result.approval_request.requested_tool,
                "requested_entities": result.approval_request.requested_entities,
                "reason": result.approval_request.reason,
            },
        )
    if result.simulation_result is not None:
        record_audit_event(
            correlation_id=result.correlation_id,
            event_type="tool_simulation_completed",
            source="agent.chat",
            status=result.simulation_result.status,
            details={
                "tool_name": result.simulation_result.tool_name,
                "mode": result.simulation_result.mode,
                "risk_decision": result.simulation_result.risk_decision,
                "request_payload": (
                    result.simulation_result.request.payload
                    if result.simulation_result.request is not None
                    else None
                ),
            },
        )


@router.get("/tools", response_model=list[ToolResponse])
async def get_tools() -> list[ToolResponse]:
    """Return the approved enterprise MCP tool catalog."""

    # This endpoint is like a read-only tool catalog page for clients.
    return [_to_tool_response(tool) for tool in list_tools()]


@router.get("/mcp/config", response_model=McpServerConfigResponse)
async def get_mcp_config() -> McpServerConfigResponse:
    """Return safe MCP runtime configuration for diagnostics."""

    return _to_mcp_config_response(load_mcp_config())


@router.get("/mcp/executor", response_model=McpExecutorDiagnosticsResponse)
async def get_mcp_executor() -> McpExecutorDiagnosticsResponse:
    """Return safe diagnostics for the active MCP executor."""

    return _to_mcp_executor_diagnostics_response(
        get_mcp_executor_diagnostics(load_mcp_config())
    )


@router.get("/foundry/agent-adapter", response_model=AgentAdapterResponse)
async def get_foundry_agent_adapter() -> AgentAdapterResponse:
    """Return the active agent runtime adapter for diagnostics."""

    return _to_agent_adapter_response(get_agent_adapter())


@router.post("/agent/chat", response_model=AgentChatResponse)
async def chat_with_agent(request: AgentChatRequest) -> AgentChatResponse:
    """Accept a user message through the safe agent shell."""

    # Route through an adapter so a Foundry/Agent Framework runtime can replace
    # the local rule-based shell without changing this API endpoint.
    # Resolve correlation once at the API boundary so planning, approval, and
    # MCP simulation can all share the same trace identifier.
    correlation_id = resolve_correlation_id(request.correlation_id)
    agent_adapter = get_agent_adapter()
    result = agent_adapter.chat(
        user_message=request.user_message,
        correlation_id=correlation_id,
        simulate_when_ready=request.simulate_when_ready,
    )
    _audit_chat_result(result)
    return _to_agent_chat_response(result)


@router.post("/approvals/{approval_id}/decision", response_model=ApprovalDecisionResponse)
async def decide_approval(
    approval_id: str,
    request: ApprovalDecisionRequest,
) -> ApprovalDecisionResponse:
    """Approve or reject a pending high-risk action request."""

    # Step 3G records the human decision only. Step 3H can use approved
    # decisions to execute the original high-risk MCP action.
    decision = decide_approval_request(
        approval_id=approval_id,
        decision=request.decision,
        reviewer=request.reviewer,
        comment=request.comment,
    )
    if decision is None:
        raise HTTPException(status_code=404, detail=f"Approval request not found: {approval_id}")

    record_audit_event(
        correlation_id=decision.correlation_id,
        event_type="approval_decision_recorded",
        source="approvals.decision",
        status=decision.status,
        details={
            "approval_id": decision.approval_id,
            "requested_tool": decision.requested_tool,
            "decision": decision.decision,
            "reviewer": decision.reviewer,
            "comment": decision.comment,
        },
    )
    return _to_approval_decision_response(decision)


@router.post("/approvals/{approval_id}/execute", response_model=ApprovalExecutionResponse)
async def execute_approved_action(approval_id: str) -> ApprovalExecutionResponse:
    """Execute a high-risk action only after its approval request is approved."""

    approval_request = get_approval_request(approval_id)
    if approval_request is None:
        raise HTTPException(status_code=404, detail=f"Approval request not found: {approval_id}")

    approval_decision = get_approval_decision(approval_id)
    if approval_decision is None:
        raise HTTPException(status_code=409, detail=f"Approval request is still pending: {approval_id}")

    if approval_decision.decision != "approved":
        raise HTTPException(status_code=409, detail=f"Approval request was rejected: {approval_id}")

    tool = get_tool(approval_request.requested_tool)
    if tool is None:
        raise HTTPException(
            status_code=404,
            detail=f"Tool not found for approval request: {approval_request.requested_tool}",
        )

    risk_decision = evaluate_tool_risk(tool)
    simulation_result = simulate_mcp_tool_after_approval(
        tool=tool,
        risk_decision=risk_decision,
        correlation_id=approval_request.correlation_id,
        approval_id=approval_id,
        entities=approval_request.requested_entities,
    )
    record_audit_event(
        correlation_id=approval_request.correlation_id,
        event_type="approved_action_executed",
        source="approvals.execute",
        status=simulation_result.status,
        details={
            "approval_id": approval_id,
            "approval_status": approval_decision.status,
            "tool_name": simulation_result.tool_name,
            "risk_decision": simulation_result.risk_decision,
            "mode": simulation_result.mode,
            "request_payload": (
                simulation_result.request.payload
                if simulation_result.request is not None
                else None
            ),
        },
    )
    return _to_approval_execution_response(
        approval_id=approval_id,
        approval_status=approval_decision.status,
        simulation_result=simulation_result,
    )


@router.get("/audit/{correlation_id}", response_model=list[AuditEventResponse])
async def get_audit_events(correlation_id: str) -> list[AuditEventResponse]:
    """Return audit events for one correlation ID."""

    return [_to_audit_event_response(event) for event in list_audit_events(correlation_id)]


@router.get("/foundry/traces/{correlation_id}", response_model=list[FoundryTraceResponse])
async def get_foundry_traces(correlation_id: str) -> list[FoundryTraceResponse]:
    """Return Foundry-style trace records for one correlation ID."""

    audit_events = list_audit_events(correlation_id)
    traces = audit_events_to_foundry_traces(audit_events)
    return [_to_foundry_trace_response(trace) for trace in traces]


@router.get(
    "/observability/appinsights/{correlation_id}",
    response_model=list[AppInsightsEventResponse],
)
async def get_appinsights_events(correlation_id: str) -> list[AppInsightsEventResponse]:
    """Return Application Insights custom event envelopes for one correlation ID."""

    audit_events = list_audit_events(correlation_id)
    traces = audit_events_to_foundry_traces(audit_events)
    appinsights_events = traces_to_appinsights_events(traces)
    return [_to_appinsights_event_response(event) for event in appinsights_events]


@router.get("/foundry/evaluations/safety-cases", response_model=list[EvaluationCaseResponse])
async def get_evaluation_cases() -> list[EvaluationCaseResponse]:
    """Return local Foundry-style evaluation cases for safe agent behavior."""

    return [_to_evaluation_case_response(case) for case in list_evaluation_cases()]


@router.post("/foundry/evaluations/run-local", response_model=list[EvaluationResultResponse])
async def run_local_evaluations() -> list[EvaluationResultResponse]:
    """Run the local Foundry-style evaluation suite."""

    return [_to_evaluation_result_response(result) for result in run_local_evaluation_suite()]


@router.get("/operations/readiness", response_model=ReadinessReportResponse)
async def get_operations_readiness() -> ReadinessReportResponse:
    """Return local operational readiness status."""

    return _to_readiness_report_response(run_readiness_checks())


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

    # TEMPORARY ENDPOINT: useful for learning and tests. Later this can become
    # an integration test helper or call the real Logic Apps MCP server.
    tool = get_tool(tool_name)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")

    correlation_id = resolve_correlation_id(request.correlation_id if request else None)
    risk_decision = evaluate_tool_risk(tool)
    return _to_simulation_response(simulate_mcp_tool(tool, risk_decision, correlation_id))
