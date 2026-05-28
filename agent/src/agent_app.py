"""Agent orchestration entry point.

Microsoft Agent Framework and Foundry-specific code will stay isolated here so the
API, MCP adapter, and tool policies remain stable as SDKs evolve.
"""

import re
from dataclasses import dataclass

from approvals.requests import ApprovalRequest, create_approval_request
from mcp.client import McpSimulationResult, simulate_mcp_tool
from tools.registry import get_tool
from tools.risk_policy import ExecutionDecision
from tools.risk_policy import evaluate_tool_risk


# **************** TEMPORARY AGENT SCAFFOLD ****************
# These lightweight classes and helper functions support the learning project
# before the real Microsoft Agent Framework / Foundry agent is wired in.
# Later, the production agent can replace intent detection, entity extraction,
# and planning logic while preserving the same API contracts.
# ***********************************************************


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
    """Safe placeholder result returned by the agent shell."""

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


INTENT_TOOL_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    # These rules are intentionally simple and transparent for the learning
    # project. A Foundry-hosted agent can replace this later while returning
    # the same selected tool and planned action shape.
    (("order",), "getOrderStatus"),
    (("invoice", "validate"), "validateInvoice"),
    (("shipment", "status"), "checkShipmentStatus"),
    (("supplier", "notify"), "sendSupplierNotification"),
    (("approval", "request"), "createApprovalRequest"),
    (("servicenow", "ticket"), "createServiceNowTicket"),
    (("integration", "run", "status"), "queryIntegrationRunStatus"),
    (("correlation", "status"), "queryIntegrationRunStatus"),
)

REQUIRED_ENTITIES_BY_TOOL: dict[str, tuple[str, ...]] = {
    # Readiness is tool-specific. A shipment ID should not make an order lookup
    # executable, and an order ID should not make a shipment action executable.
    "getOrderStatus": ("order_id",),
    "validateInvoice": ("invoice_id",),
    "checkShipmentStatus": ("shipment_id",),
    "sendSupplierNotification": ("shipment_id",),
    "createApprovalRequest": (),
    "createServiceNowTicket": (),
    "queryIntegrationRunStatus": ("correlation_id",),
}


# **************** TEMPORARY UNTIL REAL AGENT PLANNER ****************
# A Foundry-hosted agent should eventually replace this rule-based detector.
# Keep the output contract: selected approved MCP tool name or None.
# ********************************************************************
def detect_tool_from_message(user_message: str) -> str | None:
    """Map a simple user message to an approved tool name using transparent rules."""

    normalized_message = user_message.lower()
    for required_terms, tool_name in INTENT_TOOL_RULES:
        if all(term in normalized_message for term in required_terms):
            return tool_name

    return None


# **************** TEMPORARY UNTIL REAL ENTITY EXTRACTION ****************
# A production agent can use structured extraction or model output here.
# Keep the output contract: dict of business entity names to values.
# ***********************************************************************
def extract_entities(user_message: str) -> dict[str, str]:
    """Extract simple business identifiers from a user message."""

    entity_patterns = {
        "order_id": r"\bORD-\d+\b",
        "invoice_id": r"\bINV-\d+\b",
        "shipment_id": r"\bSHIP-\d+\b",
        "ticket_id": r"\bTKT-\d+\b",
        "correlation_id": r"\b(?:[a-z]+-)?corr-[a-z0-9-]+\b",
    }

    entities: dict[str, str] = {}
    for entity_name, pattern in entity_patterns.items():
        match = re.search(pattern, user_message, flags=re.IGNORECASE)
        if match:
            entities[entity_name] = match.group(0)

    return entities


# **************** KEEP, BUT MAY MOVE TO TOOL CONTRACTS ****************
# The required-entity rule is real governance logic. Later it may move into
# ToolContract metadata or external policy configuration instead of this map.
# *********************************************************************
def get_missing_entities(tool_name: str, entities: dict[str, str]) -> list[str]:
    """Return required entity names that are missing for a selected tool."""

    required_entities = REQUIRED_ENTITIES_BY_TOOL.get(tool_name, ())
    return [entity_name for entity_name in required_entities if entity_name not in entities]


# **************** TEMPORARY AGENT ENTRYPOINT ****************
# This function is the current stand-in for the future Agent Framework /
# Foundry orchestration layer. Later, the real agent should still produce the
# same planned action, simulation result, or approval request response shapes.
# ************************************************************
def handle_chat_message(
    user_message: str,
    correlation_id: str,
    simulate_when_ready: bool = False,
) -> AgentChatResult:
    """Accept a user message and suggest a matching approved tool when obvious."""

    selected_tool = detect_tool_from_message(user_message)
    entities = extract_entities(user_message)
    if selected_tool is None:
        # No catalog match means the agent should ask for clarification instead
        # of inventing a backend action.
        return AgentChatResult(
            correlation_id=correlation_id,
            status="needs_clarification",
            message=(
                "Agent shell received your request, but no approved tool matched it yet. "
                "Try an order, invoice, shipment, supplier, approval, ticket, or integration "
                "run-status request."
            ),
            tool_called=False,
            selected_tool=None,
            risk_decision=None,
            approval_required=None,
            entities=entities,
            planned_action=None,
            simulation_result=None,
            approval_request=None,
        )

    tool = get_tool(selected_tool)
    if tool is None:
        # This is a defensive governance check. Intent detection should only
        # return catalog tools, but execution still verifies the registry.
        return AgentChatResult(
            correlation_id=correlation_id,
            status="unsupported_tool",
            message="The message matched a tool rule, but the tool is not in the approved catalog.",
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
    missing_entities = get_missing_entities(tool.name, entities)
    # The planned action is the handoff object between natural-language
    # understanding and governed MCP execution.
    planned_action = PlannedAction(
        tool_name=tool.name,
        entities=entities,
        risk_decision=risk_decision.decision.value,
        approval_required=risk_decision.approval_required,
        ready_for_simulation=not missing_entities,
        missing_entities=missing_entities,
    )
    if not simulate_when_ready:
        # By default chat only plans. The caller must explicitly opt in before
        # the agent crosses from planning into mock execution.
        return AgentChatResult(
            correlation_id=correlation_id,
            status="tool_selected",
            message=(
                f"Agent shell selected approved tool '{tool.name}'. Execution is not automatic yet; "
                "set simulate_when_ready=true to test mock execution from chat."
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

    if missing_entities:
        # A selected tool is not enough. The agent needs the specific business
        # identifiers required by that tool before simulation or approval.
        return AgentChatResult(
            correlation_id=correlation_id,
            status="missing_required_entities",
            message=(
                f"Agent shell selected approved tool '{tool.name}', but mock simulation "
                f"needs: {', '.join(missing_entities)}."
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
        # High-risk actions become approval requests instead of MCP calls.
        # This keeps valid business requests reviewable without executing them.
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
                f"Agent shell selected approved tool '{tool.name}', but this action requires "
                "human approval before MCP simulation. A pending approval request was created."
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

    simulation_result = simulate_mcp_tool(tool, risk_decision, correlation_id)

    # Only ready, allowed actions reach the MCP boundary from chat.
    return AgentChatResult(
        correlation_id=correlation_id,
        status=simulation_result.status,
        message=(
            f"Agent shell selected approved tool '{tool.name}' and completed mock MCP simulation."
        ),
        tool_called=True,
        selected_tool=tool.name,
        risk_decision=risk_decision.decision.value,
        approval_required=risk_decision.approval_required,
        entities=entities,
        planned_action=planned_action,
        simulation_result=simulation_result,
        approval_request=None,
    )
