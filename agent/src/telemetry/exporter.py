"""Azure Monitor OpenTelemetry configuration and governed audit export."""

import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from config import Settings, get_settings
from foundry.tracing import audit_event_to_foundry_trace
from telemetry.appinsights import trace_to_appinsights_event

if TYPE_CHECKING:
    from audit.events import AuditEvent


LOGGER_NAME = "enterprise.integration.audit"
LOGGER = logging.getLogger(LOGGER_NAME)


@dataclass(frozen=True)
class ObservabilityConfiguration:
    """Summary of the configured observability export."""

    enabled: bool
    service_name: str
    exporter: str


def configure_observability(
    settings: Settings | None = None,
) -> ObservabilityConfiguration:
    """Configure Azure Monitor when an Application Insights connection is available."""

    resolved_settings = settings or get_settings()
    if not resolved_settings.applicationinsights_connection_string:
        return ObservabilityConfiguration(
            enabled=False,
            service_name=resolved_settings.agent_name,
            exporter="disabled",
        )

    from azure.identity import DefaultAzureCredential
    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor(
        connection_string=resolved_settings.applicationinsights_connection_string,
        credential=DefaultAzureCredential(),
        enable_live_metrics=False,
        logger_name=LOGGER_NAME,
    )
    LOGGER.setLevel(logging.INFO)
    return ObservabilityConfiguration(
        enabled=True,
        service_name=resolved_settings.agent_name,
        exporter="azure_monitor_opentelemetry",
    )


def emit_audit_event(event: "AuditEvent") -> None:
    """Emit one governed audit event as a structured Azure Monitor log."""

    trace = audit_event_to_foundry_trace(event)
    envelope = trace_to_appinsights_event(trace)
    dimensions = _build_dimensions(event, envelope.properties)
    log = LOGGER.warning if envelope.severity == "warning" else LOGGER.info
    log(
        envelope.name,
        extra=dimensions,
    )


def _build_dimensions(event: "AuditEvent", properties: dict[str, Any]) -> dict[str, Any]:
    """Build query-friendly dimensions without flattening arbitrary payload values."""

    dimensions: dict[str, Any] = {
        "event_id": event.event_id,
        "correlation_id": event.correlation_id,
        "event_type": event.event_type,
        "source": event.source,
        "status": event.status,
        "span_kind": properties["span_kind"],
        "details_json": json.dumps(event.details, separators=(",", ":"), default=str),
    }
    for name in (
        "selected_tool",
        "tool_name",
        "requested_tool",
        "risk_decision",
        "approval_required",
        "approval_id",
        "decision",
        "mode",
    ):
        value = event.details.get(name)
        if value is not None:
            dimensions[name] = value
    return dimensions
