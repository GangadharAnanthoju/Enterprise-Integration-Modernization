"""Shared contracts for enterprise MCP tool metadata."""

from dataclasses import dataclass
from enum import StrEnum


class RiskLevel(StrEnum):
    """Business risk level for an AI-callable enterprise tool."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ToolContract:
    """Metadata describing one approved MCP tool."""

    # frozen=True makes tool definitions read-only once created.
    # That helps treat the registry like a controlled catalog.
    name: str
    description: str
    business_domain: str
    backend_system: str
    risk_level: RiskLevel
    approval_required: bool
    owner: str
    version: str
    operational_impact: str
    input_schema_ref: str
    output_schema_ref: str
