"""Agent orchestration entry point.

Microsoft Agent Framework and Foundry-specific code will stay isolated here so the
API, MCP adapter, and tool policies remain stable as SDKs evolve.
"""

import re

from agent_contracts import AgentChatResult
from agent_execution import execute_planned_action


INTENT_TOOL_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    # Local deterministic planner rules. Foundry mode uses the same selected
    # tool and planned action shape after model-based planning.
    (("order",), "getOrderStatus"),
    (("invoice", "validate"), "validateInvoice"),
    (("shipment", "status"), "checkShipmentStatus"),
    (("supplier", "notify"), "sendSupplierNotification"),
    (("approval", "request"), "createApprovalRequest"),
    (("servicenow", "ticket"), "createServiceNowTicket"),
    (("integration", "run", "status"), "queryIntegrationRunStatus"),
    (("correlation", "status"), "queryIntegrationRunStatus"),
)

def detect_tool_from_message(user_message: str) -> str | None:
    """Map a simple user message to an approved tool name using transparent rules."""

    normalized_message = user_message.lower()
    for required_terms, tool_name in INTENT_TOOL_RULES:
        if all(term in normalized_message for term in required_terms):
            return tool_name

    return None


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
            "set simulate_when_ready=true to execute the approved MCP path from chat."
        ),
        missing_entities_message=None,
        unsupported_tool_message=(
            "The message matched a tool rule, but the tool is not in the approved catalog."
        ),
    )
