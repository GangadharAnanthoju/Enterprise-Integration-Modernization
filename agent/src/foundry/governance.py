"""Foundry governance hooks and policy checks."""

from dataclasses import dataclass

from approvals.requests import APPROVAL_DECISIONS, APPROVAL_REQUESTS
from audit.events import AUDIT_EVENTS, AuditEvent
from config import Settings
from config_validation import validate_environment
from foundry.agent_definition import validate_foundry_agent_definition
from foundry.agent_adapter import get_agent_adapter
from foundry.registration_plan import run_foundry_registration_preflight
from foundry.tracing import audit_event_to_foundry_trace
from foundry.tool_registration import validate_foundry_tool_registrations
from maf_runtime.enterprise_agent import validate_enterprise_maf_agent_skeleton
from mcp.client import load_mcp_config
from mcp.schemas import McpExecutionMode
from tools.registry import list_tools
from tools.risk_policy import evaluate_tool_name


@dataclass(frozen=True)
class ReadinessCheck:
    """One operational readiness check result."""

    name: str
    status: str
    details: str


@dataclass(frozen=True)
class ReadinessReport:
    """Summary of local operational readiness checks."""

    status: str
    checks: list[ReadinessCheck]


def run_readiness_checks(settings: Settings | None = None) -> ReadinessReport:
    """Run local operational readiness checks for the governed agent shell."""

    checks = [
        _check_tool_catalog(),
        _check_high_risk_policy(),
        _check_approval_store(),
        _check_audit_store(),
        _check_observability_projection(),
        _check_mcp_runtime_config(settings),
        _check_agent_runtime_adapter(),
        _check_foundry_agent_definition(),
        _check_foundry_tool_registration(),
        _check_maf_agent_skeleton(settings),
        _check_foundry_registration_preflight(settings),
        _check_environment_validation(settings),
    ]
    report_status = "ready" if all(check.status == "pass" for check in checks) else "needs_attention"
    return ReadinessReport(status=report_status, checks=checks)


def _check_tool_catalog() -> ReadinessCheck:
    tools = list_tools()
    if tools:
        return ReadinessCheck(
            name="tool_catalog",
            status="pass",
            details=f"{len(tools)} approved MCP tools are registered.",
        )

    return ReadinessCheck(
        name="tool_catalog",
        status="fail",
        details="No approved MCP tools are registered.",
    )


def _check_high_risk_policy() -> ReadinessCheck:
    decision = evaluate_tool_name("sendSupplierNotification")
    if decision.approval_required and decision.decision == "require_approval":
        return ReadinessCheck(
            name="high_risk_policy",
            status="pass",
            details="High-risk supplier notification requires approval.",
        )

    return ReadinessCheck(
        name="high_risk_policy",
        status="fail",
        details="High-risk supplier notification is not blocked for approval.",
    )


def _check_approval_store() -> ReadinessCheck:
    if isinstance(APPROVAL_REQUESTS, dict) and isinstance(APPROVAL_DECISIONS, dict):
        return ReadinessCheck(
            name="approval_store",
            status="pass",
            details="Local approval request and decision stores are available.",
        )

    return ReadinessCheck(
        name="approval_store",
        status="fail",
        details="Approval stores are not available.",
    )


def _check_audit_store() -> ReadinessCheck:
    if isinstance(AUDIT_EVENTS, list):
        return ReadinessCheck(
            name="audit_store",
            status="pass",
            details="Local audit event store is available.",
        )

    return ReadinessCheck(
        name="audit_store",
        status="fail",
        details="Audit event store is not available.",
    )


def _check_observability_projection() -> ReadinessCheck:
    sample_event = AuditEvent(
        event_id="readiness-sample",
        correlation_id="readiness-correlation",
        event_type="agent_chat_planned",
        source="readiness",
        status="completed",
        details={"selected_tool": "getOrderStatus"},
    )
    trace = audit_event_to_foundry_trace(sample_event)
    if trace.span_kind == "agent" and trace.correlation_id == sample_event.correlation_id:
        return ReadinessCheck(
            name="observability_projection",
            status="pass",
            details="Audit events can be projected into Foundry-style traces.",
        )

    return ReadinessCheck(
        name="observability_projection",
        status="fail",
        details="Audit events could not be projected into Foundry-style traces.",
    )


def _check_mcp_runtime_config(settings: Settings | None = None) -> ReadinessCheck:
    config = load_mcp_config(settings)
    if config.mode == McpExecutionMode.MOCK and config.server_name:
        return ReadinessCheck(
            name="mcp_runtime_config",
            status="pass",
            details=(
                f"MCP runtime is configured for {config.mode.value} mode using "
                f"server name '{config.server_name}'."
            ),
        )

    if config.mode == McpExecutionMode.REMOTE and config.endpoint_configured:
        return ReadinessCheck(
            name="mcp_runtime_config",
            status="pass",
            details=(
                f"MCP runtime is configured for remote mode using "
                f"server name '{config.server_name}'."
            ),
        )

    return ReadinessCheck(
        name="mcp_runtime_config",
        status="fail",
        details="MCP runtime configuration is incomplete.",
    )


def _check_agent_runtime_adapter() -> ReadinessCheck:
    adapter = get_agent_adapter()
    if adapter.name and adapter.runtime and adapter.implementation_status:
        return ReadinessCheck(
            name="agent_runtime_adapter",
            status="pass",
            details=(
                f"Active agent adapter is '{adapter.name}' "
                f"with runtime '{adapter.runtime}'."
            ),
        )

    return ReadinessCheck(
        name="agent_runtime_adapter",
        status="fail",
        details="Agent runtime adapter metadata is incomplete.",
    )


def _check_foundry_agent_definition() -> ReadinessCheck:
    missing = validate_foundry_agent_definition()
    if not missing:
        return ReadinessCheck(
            name="foundry_agent_definition",
            status="pass",
            details="Local Foundry agent definition skeleton is complete.",
        )

    return ReadinessCheck(
        name="foundry_agent_definition",
        status="fail",
        details=f"Foundry agent definition needs attention: {'; '.join(missing)}.",
    )


def _check_foundry_tool_registration() -> ReadinessCheck:
    missing = validate_foundry_tool_registrations()
    if not missing:
        return ReadinessCheck(
            name="foundry_tool_registration",
            status="pass",
            details="Foundry-facing tool registration metadata is complete.",
        )

    return ReadinessCheck(
        name="foundry_tool_registration",
        status="fail",
        details=f"Foundry tool registration metadata needs attention: {'; '.join(missing)}.",
    )


def _check_maf_agent_skeleton(settings: Settings | None = None) -> ReadinessCheck:
    missing = validate_enterprise_maf_agent_skeleton(settings)
    if not missing:
        return ReadinessCheck(
            name="maf_agent_skeleton",
            status="pass",
            details="Local Microsoft Agent Framework skeleton is configured.",
        )

    return ReadinessCheck(
        name="maf_agent_skeleton",
        status="fail",
        details=f"MAF agent skeleton needs attention: {'; '.join(missing)}.",
    )


def _check_foundry_registration_preflight(settings: Settings | None = None) -> ReadinessCheck:
    preflight = run_foundry_registration_preflight(settings)
    if preflight.status == "ready":
        return ReadinessCheck(
            name="foundry_registration_preflight",
            status="pass",
            details="Foundry registration preflight is ready.",
        )

    return ReadinessCheck(
        name="foundry_registration_preflight",
        status="fail",
        details=f"Foundry registration preflight needs attention: {'; '.join(preflight.missing)}.",
    )


def _check_environment_validation(settings: Settings | None = None) -> ReadinessCheck:
    report = validate_environment(settings)
    if report.status == "ready":
        return ReadinessCheck(
            name="environment_validation",
            status="pass",
            details="Environment settings are valid for the selected runtime mode.",
        )

    failed_checks = [check.name for check in report.checks if check.status == "fail"]
    return ReadinessCheck(
        name="environment_validation",
        status="fail",
        details=f"Environment settings need attention: {', '.join(failed_checks)}.",
    )
