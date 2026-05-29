"""Local preflight for Microsoft Agent Framework and Foundry registration."""

from dataclasses import dataclass

from config import Settings, get_settings
from foundry.agent_definition import (
    FoundryAgentDefinition,
    load_foundry_agent_definition,
    validate_foundry_agent_definition,
)
from foundry.tool_registration import validate_foundry_tool_registrations


@dataclass(frozen=True)
class FoundryRegistrationPlan:
    """Reviewable registration inputs for the future Foundry agent."""

    agent_name: str
    display_name: str
    project_endpoint: str | None
    model_deployment_name: str | None
    framework: str
    target_runtime: str
    instructions_path: str
    tool_strategy: str
    publish_after_registration: bool


@dataclass(frozen=True)
class FoundryRegistrationPreflight:
    """Registration preflight result."""

    status: str
    plan: FoundryRegistrationPlan
    missing: list[str]


def build_foundry_registration_plan(
    settings: Settings | None = None,
    definition: FoundryAgentDefinition | None = None,
) -> FoundryRegistrationPlan:
    """Build a local registration plan without calling Foundry."""

    resolved_settings = settings or get_settings()
    resolved_definition = definition or load_foundry_agent_definition()

    return FoundryRegistrationPlan(
        agent_name=resolved_settings.foundry_agent_name,
        display_name="Enterprise Integration Modernization Agent",
        project_endpoint=resolved_settings.foundry_project_endpoint,
        model_deployment_name=resolved_settings.model_deployment_name,
        framework="microsoft_agent_framework",
        target_runtime="microsoft_foundry",
        instructions_path=resolved_definition.instruction_source,
        tool_strategy=(
            "Attach approved MCP tool layer after the MAF agent is created; "
            "keep FastAPI as the enterprise control plane."
        ),
        publish_after_registration=False,
    )


def run_foundry_registration_preflight(
    settings: Settings | None = None,
    definition: FoundryAgentDefinition | None = None,
) -> FoundryRegistrationPreflight:
    """Validate local inputs needed before creating the real Foundry agent."""

    resolved_settings = settings or get_settings()
    resolved_definition = definition or load_foundry_agent_definition()
    plan = build_foundry_registration_plan(resolved_settings, resolved_definition)

    missing: list[str] = []
    if not plan.project_endpoint:
        missing.append("FOUNDRY_PROJECT_ENDPOINT is required")
    if not plan.model_deployment_name:
        missing.append("MODEL_DEPLOYMENT_NAME is required")
    if not plan.agent_name:
        missing.append("FOUNDRY_AGENT_NAME is required")
    if plan.agent_name != resolved_definition.name:
        missing.append("FOUNDRY_AGENT_NAME must match the local agent definition name")
    if "framework: microsoft_agent_framework" not in resolved_definition.raw_text:
        missing.append("agent definition must declare Microsoft Agent Framework")

    missing.extend(validate_foundry_agent_definition(resolved_definition))
    missing.extend(validate_foundry_tool_registrations())

    status = "ready" if not missing else "needs_attention"
    return FoundryRegistrationPreflight(status=status, plan=plan, missing=missing)
