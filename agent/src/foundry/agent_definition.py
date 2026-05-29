"""Local Foundry agent definition checks.

The YAML file in ``foundry/agent-definitions`` is a design skeleton for future
Foundry registration. This module keeps that skeleton visible to Python tests
and readiness checks without requiring a live Foundry project.
"""

from dataclasses import dataclass
from pathlib import Path

from tools.registry import list_tools


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_AGENT_DEFINITION_PATH = (
    REPO_ROOT
    / "foundry"
    / "agent-definitions"
    / "enterprise-integration-agent.yaml"
)


@dataclass(frozen=True)
class FoundryAgentDefinition:
    """Important fields from the local Foundry agent definition skeleton."""

    path: Path
    name: str
    instruction_source: str
    approved_tool_names: tuple[str, ...]
    raw_text: str

    @property
    def instruction_path(self) -> Path:
        """Resolve the instruction source relative to the repository root."""

        return REPO_ROOT / self.instruction_source


def load_foundry_agent_definition(
    path: Path = DEFAULT_AGENT_DEFINITION_PATH,
) -> FoundryAgentDefinition:
    """Load the local Foundry agent definition skeleton."""

    raw_text = path.read_text(encoding="utf-8")
    return FoundryAgentDefinition(
        path=path,
        name=_extract_scalar(raw_text, "name"),
        instruction_source=_extract_scalar(raw_text, "source"),
        approved_tool_names=tuple(
            tool.name for tool in list_tools() if f"name: {tool.name}" in raw_text
        ),
        raw_text=raw_text,
    )


def validate_foundry_agent_definition(
    definition: FoundryAgentDefinition | None = None,
) -> list[str]:
    """Return human-readable configuration gaps for the local agent definition."""

    resolved_definition = definition or load_foundry_agent_definition()
    missing: list[str] = []

    if resolved_definition.name != "enterprise-integration-agent":
        missing.append("agent name must be enterprise-integration-agent")

    if not resolved_definition.instruction_source:
        missing.append("instruction source is missing")
    elif not resolved_definition.instruction_path.exists():
        missing.append(f"instruction file not found: {resolved_definition.instruction_source}")

    expected_tools = {tool.name for tool in list_tools()}
    configured_tools = set(resolved_definition.approved_tool_names)
    missing_tools = sorted(expected_tools - configured_tools)
    if missing_tools:
        missing.append(f"approved tool placeholders missing: {', '.join(missing_tools)}")

    required_phrases = [
        "target: microsoft_foundry",
        "executionBoundary: MCP",
        "backendImplementation: Logic Apps Standard workflows",
        "toolRegistrySource: agent/src/tools/registry.py",
        "riskPolicySource: agent/src/tools/risk_policy.py",
    ]
    for phrase in required_phrases:
        if phrase not in resolved_definition.raw_text:
            missing.append(f"agent definition missing: {phrase}")

    return missing


def _extract_scalar(raw_text: str, key: str) -> str:
    """Extract a simple top-level-ish YAML scalar without adding a YAML dependency."""

    prefix = f"{key}:"
    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped.removeprefix(prefix).strip()
    return ""
