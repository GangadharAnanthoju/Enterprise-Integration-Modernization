"""Application Insights integration wrapper."""

from dataclasses import dataclass
from typing import Any

from foundry.tracing import FoundryTraceRecord


# **************** TEMPORARY APP INSIGHTS PROJECTION ****************
# Active now as a local envelope builder. Later this module can send these
# events through Azure Monitor OpenTelemetry or the Application Insights SDK.
# ***************************************************************


@dataclass(frozen=True)
class AppInsightsCustomEvent:
    """Application Insights custom event-shaped view of a trace record."""

    name: str
    operation_id: str
    severity: str
    properties: dict[str, Any]


def trace_to_appinsights_event(trace: FoundryTraceRecord) -> AppInsightsCustomEvent:
    """Convert a Foundry-style trace record into an App Insights event shape."""

    severity = "warning" if trace.status in {"approval_required", "rejected"} else "information"
    return AppInsightsCustomEvent(
        name=f"enterprise.integration.{trace.span_name}",
        operation_id=trace.correlation_id,
        severity=severity,
        properties={
            "trace_id": trace.trace_id,
            "span_kind": trace.span_kind,
            "source": trace.source,
            "status": trace.status,
            **trace.attributes,
        },
    )


def traces_to_appinsights_events(
    traces: list[FoundryTraceRecord],
) -> list[AppInsightsCustomEvent]:
    """Convert trace records into Application Insights custom event envelopes."""

    return [trace_to_appinsights_event(trace) for trace in traces]
