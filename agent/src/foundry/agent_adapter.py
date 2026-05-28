"""Agent runtime adapter boundary.

This module is the replacement point for the future Microsoft Foundry-hosted
agent. FastAPI should depend on this adapter contract, not directly on the
temporary rule-based planner.
"""

from dataclasses import dataclass
from typing import Protocol

from agent_app import AgentChatResult, handle_chat_message


class AgentRuntimeAdapter(Protocol):
    """Stable interface for local and future Foundry agent runtimes."""

    name: str
    runtime: str
    implementation_status: str

    def chat(
        self,
        user_message: str,
        correlation_id: str,
        simulate_when_ready: bool = False,
    ) -> AgentChatResult:
        """Plan or execute a governed chat request."""


@dataclass(frozen=True)
class LocalRuleBasedAgentAdapter:
    """Temporary adapter around the learning-project rule-based agent shell."""

    name: str = "local-rule-based-agent"
    runtime: str = "local"
    implementation_status: str = "temporary_rule_based"

    def chat(
        self,
        user_message: str,
        correlation_id: str,
        simulate_when_ready: bool = False,
    ) -> AgentChatResult:
        """Delegate chat handling to the current transparent rule-based shell."""

        return handle_chat_message(
            user_message=user_message,
            correlation_id=correlation_id,
            simulate_when_ready=simulate_when_ready,
        )


def get_agent_adapter() -> AgentRuntimeAdapter:
    """Return the active agent runtime adapter.

    Today this returns a local rule-based adapter. Later this factory can read
    settings and return a Microsoft Foundry / Agent Framework adapter without
    changing FastAPI routes or public API schemas.
    """

    return LocalRuleBasedAgentAdapter()
