"""Live Foundry agent creation and invocation helpers.

This module is the first code path that can create or update a real Foundry
agent version. Tests use fake clients; production use should run only after
registration preflight passes and the user approves the live operation.
"""

import asyncio
from dataclasses import dataclass
from threading import Thread
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import AzureCliCredential
from agent_framework.foundry import FoundryAgent

from config import Settings, get_settings
from foundry.agent_definition import load_foundry_agent_definition
from foundry.registration_plan import run_foundry_registration_preflight


class FoundryAgentRegistrationError(RuntimeError):
    """Raised when live Foundry agent registration cannot safely run."""


@dataclass(frozen=True)
class FoundryAgentVersionResult:
    """Summary of a create/update agent-version operation."""

    agent_name: str
    model_deployment_name: str
    project_endpoint: str
    version: str | None
    status: str | None
    raw: dict[str, Any]


@dataclass(frozen=True)
class FoundryAgentInvocationResult:
    """Summary of a live Foundry agent invocation."""

    agent_name: str
    agent_version: str | None
    project_endpoint: str
    input_text: str
    response_text: str
    response_id: str | None
    raw: dict[str, Any]


def create_foundry_project_client(settings: Settings | None = None) -> AIProjectClient:
    """Create an Azure AI Foundry project client using Azure CLI credentials."""

    resolved_settings = settings or get_settings()
    if not resolved_settings.foundry_project_endpoint:
        raise FoundryAgentRegistrationError("FOUNDRY_PROJECT_ENDPOINT is required.")

    return AIProjectClient(
        endpoint=resolved_settings.foundry_project_endpoint,
        credential=AzureCliCredential(),
        allow_preview=True,
    )


def create_foundry_runtime_agent(settings: Settings | None = None) -> FoundryAgent:
    """Create a FoundryAgent runtime client for live invocation."""

    resolved_settings = settings or get_settings()
    if not resolved_settings.foundry_project_endpoint:
        raise FoundryAgentRegistrationError("FOUNDRY_PROJECT_ENDPOINT is required.")
    if not resolved_settings.foundry_agent_name:
        raise FoundryAgentRegistrationError("FOUNDRY_AGENT_NAME is required.")

    return FoundryAgent(
        project_endpoint=resolved_settings.foundry_project_endpoint,
        agent_name=resolved_settings.foundry_agent_name,
        agent_version=resolved_settings.foundry_agent_version,
        credential=AzureCliCredential(),
        allow_preview=True,
    )


def build_prompt_agent_definition(settings: Settings | None = None) -> PromptAgentDefinition:
    """Build the Prompt Agent definition used for Foundry create/update."""

    resolved_settings = settings or get_settings()
    if not resolved_settings.model_deployment_name:
        raise FoundryAgentRegistrationError("MODEL_DEPLOYMENT_NAME is required.")

    definition = load_foundry_agent_definition()
    instructions = definition.instruction_path.read_text(encoding="utf-8")
    return PromptAgentDefinition(
        model=resolved_settings.model_deployment_name,
        instructions=instructions,
        temperature=0.2,
    )


async def invoke_foundry_agent_message_async(
    input_text: str,
    settings: Settings | None = None,
    runtime_agent: Any | None = None,
) -> FoundryAgentInvocationResult:
    """Invoke the configured Foundry agent with a single user message."""

    resolved_settings = settings or get_settings()
    preflight = run_foundry_registration_preflight(resolved_settings)
    if preflight.status != "ready":
        raise FoundryAgentRegistrationError(
            "Foundry invocation preflight failed: " + "; ".join(preflight.missing)
        )

    agent = runtime_agent or create_foundry_runtime_agent(resolved_settings)
    response = await agent.run(input_text)
    raw = response.to_dict() if hasattr(response, "to_dict") else {}

    return FoundryAgentInvocationResult(
        agent_name=resolved_settings.foundry_agent_name,
        agent_version=resolved_settings.foundry_agent_version,
        project_endpoint=resolved_settings.foundry_project_endpoint or "",
        input_text=input_text,
        response_text=getattr(response, "text", ""),
        response_id=getattr(response, "response_id", None),
        raw=raw,
    )


def invoke_foundry_agent_message(
    input_text: str,
    settings: Settings | None = None,
    runtime_agent: Any | None = None,
) -> FoundryAgentInvocationResult:
    """Synchronously invoke the configured Foundry agent for scripts and demos."""

    coroutine = invoke_foundry_agent_message_async(
        input_text=input_text,
        settings=settings,
        runtime_agent=runtime_agent,
    )
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)

    return _run_coroutine_in_thread(coroutine)


def _run_coroutine_in_thread(coroutine: Any) -> FoundryAgentInvocationResult:
    """Run an async Foundry call from sync code that already has an event loop."""

    result: FoundryAgentInvocationResult | None = None
    error: BaseException | None = None

    def runner() -> None:
        nonlocal result, error
        try:
            result = asyncio.run(coroutine)
        except BaseException as exc:
            error = exc

    thread = Thread(target=runner, daemon=True)
    thread.start()
    thread.join()

    if error is not None:
        raise error
    if result is None:
        raise FoundryAgentRegistrationError(
            "Foundry invocation did not return a result."
        )
    return result


def create_or_update_foundry_prompt_agent_version(
    settings: Settings | None = None,
    project_client: Any | None = None,
) -> FoundryAgentVersionResult:
    """Create a new version for the configured Foundry Prompt Agent."""

    resolved_settings = settings or get_settings()
    preflight = run_foundry_registration_preflight(resolved_settings)
    if preflight.status != "ready":
        raise FoundryAgentRegistrationError(
            "Foundry registration preflight failed: " + "; ".join(preflight.missing)
        )

    client = project_client or create_foundry_project_client(resolved_settings)
    definition = build_prompt_agent_definition(resolved_settings)
    response = client.agents.create_version(
        resolved_settings.foundry_agent_name,
        definition=definition,
        metadata={
            "project": "Enterprise-Integration-Modernization",
            "framework": "microsoft_agent_framework",
            "execution_boundary": "MCP",
        },
        description="MAF-backed enterprise integration modernization agent.",
    )
    raw = response.as_dict() if hasattr(response, "as_dict") else {}

    return FoundryAgentVersionResult(
        agent_name=resolved_settings.foundry_agent_name,
        model_deployment_name=resolved_settings.model_deployment_name or "",
        project_endpoint=resolved_settings.foundry_project_endpoint or "",
        version=_first_present(raw, "version", "name", "id"),
        status=_first_present(raw, "status", "provisioning_state", "provisioningState"),
        raw=raw,
    )


def _first_present(source: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = source.get(key)
        if value is not None:
            return str(value)
    return None
