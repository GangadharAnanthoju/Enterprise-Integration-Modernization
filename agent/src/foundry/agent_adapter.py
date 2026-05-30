"""Agent runtime adapter boundary.

This module is the replacement point for the future Microsoft Foundry-hosted
agent. FastAPI should depend on this adapter contract, not directly on the
temporary rule-based planner.
"""

from dataclasses import dataclass
from typing import Callable, Protocol

from agent_app import AgentChatResult, handle_chat_message
from config import Settings, get_settings
from foundry.live_agent import FoundryAgentInvocationResult, invoke_foundry_agent_message
from maf_runtime.enterprise_agent import build_enterprise_maf_agent_skeleton


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


@dataclass(frozen=True)
class MafFoundryAgentAdapter:
    """Adapter for a Microsoft Agent Framework agent registered in Foundry."""

    name: str = "enterprise-integration-agent"
    runtime: str = "microsoft_foundry"
    implementation_status: str = "live_foundry_invocation_planning_only"
    runtime_invoker: Callable[[str], FoundryAgentInvocationResult] = invoke_foundry_agent_message

    def chat(
        self,
        user_message: str,
        correlation_id: str,
        simulate_when_ready: bool = False,
    ) -> AgentChatResult:
        """Invoke the live Foundry agent without crossing into backend execution."""

        build_enterprise_maf_agent_skeleton()
        foundry_result = self.runtime_invoker(user_message)
        return AgentChatResult(
            correlation_id=correlation_id,
            status="foundry_response",
            message=foundry_result.response_text,
            tool_called=False,
            selected_tool=None,
            risk_decision=None,
            approval_required=None,
            entities={},
            planned_action=None,
            simulation_result=None,
            approval_request=None,
        )


def get_agent_adapter(settings: Settings | None = None) -> AgentRuntimeAdapter:
    """Return the active agent runtime adapter.

    Local remains the default. Set AGENT_RUNTIME_MODE=foundry to route chat
    through the live Foundry agent while keeping backend execution disabled.
    """

    resolved_settings = settings or get_settings()
    if resolved_settings.agent_runtime_mode.lower() == "foundry":
        return MafFoundryAgentAdapter(name=resolved_settings.foundry_agent_name)

    return LocalRuleBasedAgentAdapter()
