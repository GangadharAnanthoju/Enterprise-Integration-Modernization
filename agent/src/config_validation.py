"""Environment configuration validation.

These checks answer a different question from runtime readiness: are the
settings complete and safe for the selected environment mode?
"""

from dataclasses import dataclass

from config import Settings, get_settings
from mcp.client import TOOL_ENDPOINT_SETTING_NAMES


@dataclass(frozen=True)
class EnvironmentCheck:
    """One environment validation check result."""

    name: str
    status: str
    details: str


@dataclass(frozen=True)
class EnvironmentValidationReport:
    """Summary of environment validation checks."""

    status: str
    checks: list[EnvironmentCheck]


def validate_environment(settings: Settings | None = None) -> EnvironmentValidationReport:
    """Validate the current environment settings."""

    resolved_settings = settings or get_settings()
    checks = [
        _check_agent_runtime_mode(resolved_settings),
        _check_mcp_mode(resolved_settings),
        _check_remote_mcp_endpoint(resolved_settings),
        _check_remote_mcp_auth(resolved_settings),
        _check_foundry_runtime(resolved_settings),
        _check_foundry_resource_context(resolved_settings),
        _check_appinsights(resolved_settings),
    ]
    report_status = (
        "needs_attention"
        if any(check.status == "fail" for check in checks)
        else "ready"
    )
    return EnvironmentValidationReport(status=report_status, checks=checks)


def _remote_mcp_enabled(settings: Settings) -> bool:
    return not settings.mock_mcp and settings.mcp_execution_mode == "remote"


def _check_agent_runtime_mode(settings: Settings) -> EnvironmentCheck:
    runtime_mode = settings.agent_runtime_mode.lower()
    if runtime_mode in {"local", "foundry"}:
        return EnvironmentCheck(
            name="agent_runtime_mode",
            status="pass",
            details=f"Agent runtime mode is configured for {runtime_mode}.",
        )

    return EnvironmentCheck(
        name="agent_runtime_mode",
        status="fail",
        details="AGENT_RUNTIME_MODE must be local or foundry.",
    )


def _check_mcp_mode(settings: Settings) -> EnvironmentCheck:
    if settings.mock_mcp and settings.mcp_execution_mode == "mock":
        return EnvironmentCheck(
            name="mcp_mode",
            status="pass",
            details="MCP is running in safe mock mode.",
        )

    if _remote_mcp_enabled(settings):
        return EnvironmentCheck(
            name="mcp_mode",
            status="pass",
            details="MCP is configured for remote execution mode.",
        )

    return EnvironmentCheck(
        name="mcp_mode",
        status="fail",
        details=(
            "MCP mode is inconsistent. Use MOCK_MCP=true with MCP_EXECUTION_MODE=mock "
            "or MOCK_MCP=false with MCP_EXECUTION_MODE=remote."
        ),
    )


def _check_remote_mcp_endpoint(settings: Settings) -> EnvironmentCheck:
    if not _remote_mcp_enabled(settings):
        return EnvironmentCheck(
            name="remote_mcp_endpoint",
            status="skip",
            details="Remote MCP endpoint is not required in mock mode.",
        )

    if settings.mcp_server_url:
        return EnvironmentCheck(
            name="remote_mcp_endpoint",
            status="pass",
            details="Remote MCP fallback endpoint is configured.",
        )

    configured_tool_endpoints = _configured_tool_endpoint_names(settings)
    if configured_tool_endpoints:
        return EnvironmentCheck(
            name="remote_mcp_endpoint",
            status="pass",
            details=(
                "Remote MCP per-tool endpoints are configured for: "
                f"{', '.join(configured_tool_endpoints)}."
            ),
        )

    return EnvironmentCheck(
        name="remote_mcp_endpoint",
        status="fail",
        details="Remote MCP mode requires MCP_SERVER_URL or at least one per-tool endpoint.",
    )


def _check_remote_mcp_auth(settings: Settings) -> EnvironmentCheck:
    if not _remote_mcp_enabled(settings):
        return EnvironmentCheck(
            name="remote_mcp_auth",
            status="skip",
            details="Remote MCP API key is not required in mock mode.",
        )

    if settings.mcp_api_key:
        return EnvironmentCheck(
            name="remote_mcp_auth",
            status="pass",
            details="Remote MCP API key is configured.",
        )

    if _configured_tool_endpoint_names(settings):
        return EnvironmentCheck(
            name="remote_mcp_auth",
            status="warning",
            details=(
                "Remote MCP API key is not configured. This is valid for local Logic Apps "
                "callback URLs that include a sig token."
            ),
        )

    return EnvironmentCheck(
        name="remote_mcp_auth",
        status="fail",
        details="Remote MCP mode requires MCP_API_KEY.",
    )


def _configured_tool_endpoint_names(settings: Settings) -> list[str]:
    """Return tool names that have a dedicated remote endpoint configured."""

    return [
        tool_name
        for tool_name, setting_name in TOOL_ENDPOINT_SETTING_NAMES.items()
        if getattr(settings, setting_name)
    ]


def _check_foundry_runtime(settings: Settings) -> EnvironmentCheck:
    if settings.foundry_project_endpoint and settings.model_deployment_name:
        return EnvironmentCheck(
            name="foundry_runtime",
            status="pass",
            details="Foundry runtime settings are configured.",
        )

    return EnvironmentCheck(
        name="foundry_runtime",
        status="warning",
        details="Foundry runtime settings are not fully configured yet.",
    )


def _check_foundry_resource_context(settings: Settings) -> EnvironmentCheck:
    required_values = {
        "AZURE_TENANT_ID": settings.azure_tenant_id,
        "AZURE_SUBSCRIPTION_ID": settings.azure_subscription_id,
        "AZURE_RESOURCE_GROUP": settings.azure_resource_group,
        "AZURE_AI_ACCOUNT_NAME": settings.azure_ai_account_name,
        "AZURE_AI_PROJECT_NAME": settings.azure_ai_project_name,
    }
    missing_names = [name for name, value in required_values.items() if not value]
    if not missing_names:
        return EnvironmentCheck(
            name="foundry_resource_context",
            status="pass",
            details="Foundry Azure resource context is configured.",
        )

    return EnvironmentCheck(
        name="foundry_resource_context",
        status="warning",
        details=(
            "Foundry Azure resource context is incomplete: "
            f"{', '.join(missing_names)}."
        ),
    )


def _check_appinsights(settings: Settings) -> EnvironmentCheck:
    if settings.applicationinsights_connection_string:
        return EnvironmentCheck(
            name="appinsights",
            status="pass",
            details="Application Insights export is configured.",
        )

    return EnvironmentCheck(
        name="appinsights",
        status="warning",
        details="Application Insights export is not configured yet.",
    )
