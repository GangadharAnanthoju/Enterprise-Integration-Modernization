"""Foundry-facing tool registration metadata.

The approved registry remains the source of truth. This module projects those
contracts into metadata that can later be used when registering tools in a
Foundry agent or an MCP-compatible gateway.
"""

from dataclasses import dataclass

from mcp.client import TOOL_ENDPOINT_SETTING_NAMES
from tools.contracts import ToolContract
from tools.registry import list_tools


@dataclass(frozen=True)
class FoundryToolRegistration:
    """Registration-ready metadata for one approved MCP tool."""

    name: str
    description: str
    business_domain: str
    backend_system: str
    risk_level: str
    approval_required: bool
    owner: str
    version: str
    required_entities: tuple[str, ...]
    input_schema_ref: str
    output_schema_ref: str
    endpoint_setting: str
    execution_boundary: str = "MCP"
    backend_implementation: str = "Logic Apps Standard workflow"


def build_foundry_tool_registration(tool: ToolContract) -> FoundryToolRegistration:
    """Convert an approved tool contract into Foundry-facing metadata."""

    return FoundryToolRegistration(
        name=tool.name,
        description=tool.description,
        business_domain=tool.business_domain,
        backend_system=tool.backend_system,
        risk_level=tool.risk_level.value,
        approval_required=tool.approval_required,
        owner=tool.owner,
        version=tool.version,
        required_entities=tool.required_entities,
        input_schema_ref=tool.input_schema_ref,
        output_schema_ref=tool.output_schema_ref,
        endpoint_setting=TOOL_ENDPOINT_SETTING_NAMES[tool.name].upper(),
    )


def list_foundry_tool_registrations() -> list[FoundryToolRegistration]:
    """Return registration metadata for all approved tools."""

    return [build_foundry_tool_registration(tool) for tool in list_tools()]


def validate_foundry_tool_registrations() -> list[str]:
    """Return metadata gaps that would block future Foundry tool registration."""

    registrations = list_foundry_tool_registrations()
    missing: list[str] = []

    for registration in registrations:
        if not registration.description:
            missing.append(f"{registration.name}: description is missing")
        if not registration.owner:
            missing.append(f"{registration.name}: owner is missing")
        if not registration.endpoint_setting:
            missing.append(f"{registration.name}: endpoint setting is missing")
        if registration.risk_level == "high" and not registration.approval_required:
            missing.append(f"{registration.name}: high-risk tools must require approval")
        if not registration.input_schema_ref or not registration.output_schema_ref:
            missing.append(f"{registration.name}: schema references are incomplete")

    return missing
