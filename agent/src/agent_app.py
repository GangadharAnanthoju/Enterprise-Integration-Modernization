"""Agent orchestration entry point.

Microsoft Agent Framework and Foundry-specific code will stay isolated here so the
API, MCP adapter, and tool policies remain stable as SDKs evolve.
"""

import re

from agent_contracts import AgentChatResult, PlannedAction
from agent_execution import execute_planned_action


# **************** TEMPORARY AGENT SCAFFOLD ****************
# These lightweight classes and helper functions support the learning project
# before the real Microsoft Agent Framework / Foundry agent is wired in.
# Later, the production agent can replace intent detection, entity extraction,
# and planning logic while preserving the same API contracts.
# ***********************************************************


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

    return execute_planned_action(
        selected_tool=selected_tool,
        entities=entities,
        correlation_id=correlation_id,
        simulate_when_ready=simulate_when_ready,
        plan_only_message=(
            f"Agent shell selected approved tool '{selected_tool}'. Execution is not automatic yet; "
            "set simulate_when_ready=true to test mock execution from chat."
        ),
        missing_entities_message=None,
        unsupported_tool_message=(
            "The message matched a tool rule, but the tool is not in the approved catalog."
        ),
    )
