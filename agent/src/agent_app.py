"""Agent orchestration entry point.

Microsoft Agent Framework and Foundry-specific code will stay isolated here so the
API, MCP adapter, and tool policies remain stable as SDKs evolve.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentChatResult:
    """Safe placeholder result returned by the agent shell."""

    correlation_id: str
    status: str
    message: str
    tool_called: bool


def handle_chat_message(user_message: str, correlation_id: str) -> AgentChatResult:
    """Accept a user message without selecting or executing tools yet."""

    return AgentChatResult(
        correlation_id=correlation_id,
        status="received",
        message=(
            "Agent shell received your request. Tool selection and Microsoft Agent "
            "Framework orchestration will be added in a later step."
        ),
        tool_called=False,
    )
