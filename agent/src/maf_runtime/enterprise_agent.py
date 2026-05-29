"""Local Microsoft Agent Framework skeleton for the enterprise agent.

This module does not call Foundry yet. It captures the configuration and
instruction inputs that a MAF-backed agent will need before we switch the
FastAPI adapter from the local rule-based shell to a real MAF runtime.
"""

from dataclasses import dataclass
from importlib.util import find_spec

from config import Settings, get_settings
from foundry.agent_definition import load_foundry_agent_definition


@dataclass(frozen=True)
class MafPackageStatus:
    """Availability of optional Microsoft Agent Framework packages."""

    agent_framework_available: bool
    foundry_provider_available: bool


@dataclass(frozen=True)
class EnterpriseMafAgentSkeleton:
    """Configuration shape for the future MAF-backed enterprise agent."""

    name: str
    project_endpoint: str | None
    model_deployment_name: str | None
    instructions_path: str
    instructions: str
    framework: str = "microsoft_agent_framework"
    provider: str = "agent_framework.foundry"
    tool_execution_boundary: str = "MCP"
    enterprise_control_plane: str = "FastAPI"


def get_maf_package_status() -> MafPackageStatus:
    """Return whether MAF packages are installed in the active environment."""

    agent_framework_available = find_spec("agent_framework") is not None
    foundry_provider_available = (
        find_spec("agent_framework.foundry") is not None
        if agent_framework_available
        else False
    )
    return MafPackageStatus(
        agent_framework_available=agent_framework_available,
        foundry_provider_available=foundry_provider_available,
    )


def build_enterprise_maf_agent_skeleton(
    settings: Settings | None = None,
) -> EnterpriseMafAgentSkeleton:
    """Build the local MAF skeleton from settings and the instruction file."""

    resolved_settings = settings or get_settings()
    definition = load_foundry_agent_definition()
    instructions_path = definition.instruction_path
    return EnterpriseMafAgentSkeleton(
        name=resolved_settings.foundry_agent_name,
        project_endpoint=resolved_settings.foundry_project_endpoint,
        model_deployment_name=resolved_settings.model_deployment_name,
        instructions_path=definition.instruction_source,
        instructions=instructions_path.read_text(encoding="utf-8"),
    )


def validate_enterprise_maf_agent_skeleton(
    settings: Settings | None = None,
) -> list[str]:
    """Return local configuration gaps for the future MAF agent."""

    skeleton = build_enterprise_maf_agent_skeleton(settings)
    missing: list[str] = []
    if not skeleton.name:
        missing.append("FOUNDRY_AGENT_NAME is required")
    if not skeleton.project_endpoint:
        missing.append("FOUNDRY_PROJECT_ENDPOINT is required")
    if not skeleton.model_deployment_name:
        missing.append("MODEL_DEPLOYMENT_NAME is required")
    if "approved MCP tools" not in skeleton.instructions:
        missing.append("instructions must include approved MCP tool guidance")
    if "High-risk tools must not execute directly from chat" not in skeleton.instructions:
        missing.append("instructions must include high-risk approval guidance")

    return missing
