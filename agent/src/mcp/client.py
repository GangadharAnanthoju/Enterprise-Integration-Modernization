"""MCP client adapter."""

from dataclasses import dataclass
from typing import Any

from config import Settings, get_settings
from tools.contracts import ToolContract
from tools.risk_policy import ExecutionDecision, RiskDecision
from mcp.exceptions import MissingRequiredEntitiesError
from mcp.executors import get_mcp_executor
from mcp.schemas import McpExecutionMode, McpServerConfig, McpToolRequest
from secret_store import resolve_mcp_api_key

TOOL_ENDPOINT_SETTING_NAMES: dict[str, str] = {
    "getOrderStatus": "mcp_tool_endpoint_get_order_status",
    "checkShipmentStatus": "mcp_tool_endpoint_check_shipment_status",
    "validateInvoice": "mcp_tool_endpoint_validate_invoice",
    "queryIntegrationRunStatus": "mcp_tool_endpoint_query_integration_run_status",
    "createApprovalRequest": "mcp_tool_endpoint_create_approval_request",
    "createServiceNowTicket": "mcp_tool_endpoint_create_servicenow_ticket",
    "sendSupplierNotification": "mcp_tool_endpoint_send_supplier_notification",
}


@dataclass(frozen=True)
class McpSimulationResult:
    """Normalized result returned by local or remote MCP execution."""

    tool_name: str
    correlation_id: str
    mode: str
    status: str
    risk_decision: str
    approval_required: bool
    request: McpToolRequest | None
    result: dict[str, Any] | None
    message: str


def build_mcp_request(
    tool: ToolContract,
    entities: dict[str, str],
    correlation_id: str,
) -> McpToolRequest:
    """Build a validated MCP request payload from tool metadata and entities."""

    missing_entities = [
        entity_name for entity_name in tool.required_entities if entity_name not in entities
    ]
    if missing_entities:
        raise MissingRequiredEntitiesError(tool.name, missing_entities)

    payload = {entity_name: entities[entity_name] for entity_name in tool.required_entities}
    return McpToolRequest(
        tool_name=tool.name,
        correlation_id=correlation_id,
        payload=payload,
    )


def load_mcp_config(settings: Settings | None = None) -> McpServerConfig:
    """Load runtime configuration for the MCP execution boundary."""

    resolved_settings = settings or get_settings()
    mode = (
        McpExecutionMode.MOCK
        if resolved_settings.mock_mcp
        else McpExecutionMode(resolved_settings.mcp_execution_mode)
    )
    return McpServerConfig(
        mode=mode,
        server_name=resolved_settings.mcp_server_name,
        endpoint_url=_blank_to_none(resolved_settings.mcp_server_url),
        timeout_seconds=resolved_settings.mcp_timeout_seconds,
        api_key=resolve_mcp_api_key(resolved_settings),
        tool_endpoints=_load_tool_endpoints(resolved_settings),
    )


def _load_tool_endpoints(settings: Settings) -> dict[str, str]:
    """Load optional per-tool remote endpoints from environment settings."""

    endpoints: dict[str, str] = {}
    for tool_name, setting_name in TOOL_ENDPOINT_SETTING_NAMES.items():
        endpoint_url = getattr(settings, setting_name)
        if endpoint_url:
            endpoints[tool_name] = endpoint_url

    return endpoints


def _blank_to_none(value: str | None) -> str | None:
    """Treat empty environment values as unset configuration."""

    if value is None:
        return None
    stripped_value = value.strip()
    return stripped_value or None


def simulate_mcp_tool(
    tool: ToolContract,
    risk_decision: RiskDecision,
    correlation_id: str,
    entities: dict[str, str] | None = None,
) -> McpSimulationResult:
    """Execute an MCP tool request when governance allows it."""

    mcp_request = (
        build_mcp_request(tool, entities, correlation_id)
        if entities is not None
        else None
    )

    # High-risk tools must stop here too. Direct execution helper calls should
    # respect the same policy as the chat flow.
    if risk_decision.decision == ExecutionDecision.REQUIRE_APPROVAL:
        return McpSimulationResult(
            tool_name=tool.name,
            correlation_id=correlation_id,
            mode="mock",
            status="approval_required",
            risk_decision=risk_decision.decision.value,
            approval_required=True,
            request=mcp_request,
            result=None,
            message="Tool execution stopped because this action requires approval.",
        )

    executor = get_mcp_executor(load_mcp_config())
    execution_output = executor.execute(tool, mcp_request)
    return McpSimulationResult(
        tool_name=tool.name,
        correlation_id=correlation_id,
        mode=execution_output.mode,
        status=execution_output.status,
        risk_decision=risk_decision.decision.value,
        approval_required=False,
        request=mcp_request,
        result=execution_output.result,
        message=execution_output.message,
    )


def simulate_mcp_tool_after_approval(
    tool: ToolContract,
    risk_decision: RiskDecision,
    correlation_id: str,
    approval_id: str,
    entities: dict[str, str] | None = None,
) -> McpSimulationResult:
    """Execute a high-risk MCP tool only after approval is recorded."""

    mcp_request = (
        build_mcp_request(tool, entities, correlation_id)
        if entities is not None
        else None
    )

    # Explicit approval path: this is the only place high-risk tools can move
    # past require_approval. Direct tool execution remains blocked above.
    executor = get_mcp_executor(load_mcp_config())
    execution_output = executor.execute(tool, mcp_request)
    return McpSimulationResult(
        tool_name=tool.name,
        correlation_id=correlation_id,
        mode=execution_output.mode,
        status=execution_output.status,
        risk_decision=risk_decision.decision.value,
        approval_required=False,
        request=mcp_request,
        result=execution_output.result,
        message=f"{execution_output.message} Approval: {approval_id}.",
    )
