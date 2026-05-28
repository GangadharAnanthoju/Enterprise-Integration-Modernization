"""Foundry tracing helpers."""

from dataclasses import dataclass
from typing import Any

from audit.events import AuditEvent


# **************** KEEP: FOUNDRY TRACE PROJECTION ****************
# This module maps local audit events to Foundry-style trace records. Later it
# can emit real traces to Microsoft Foundry or OpenTelemetry without changing
# the governed workflow code.
# ***************************************************************


@dataclass(frozen=True)
class FoundryTraceRecord:
    """Trace-shaped view of one governed agent workflow event."""

    trace_id: str
    correlation_id: str
    span_name: str
    span_kind: str
    status: str
    source: str
    attributes: dict[str, Any]


SPAN_KIND_BY_EVENT_TYPE: dict[str, str] = {
    "agent_chat_planned": "agent",
    "approval_request_created": "approval",
    "approval_decision_recorded": "approval",
    "approved_action_executed": "tool",
    "tool_simulation_completed": "tool",
}


def audit_event_to_foundry_trace(event: AuditEvent) -> FoundryTraceRecord:
    """Convert one audit event into a Foundry-style trace record."""

    return FoundryTraceRecord(
        trace_id=event.event_id,
        correlation_id=event.correlation_id,
        span_name=event.event_type,
        span_kind=SPAN_KIND_BY_EVENT_TYPE.get(event.event_type, "workflow"),
        status=event.status,
        source=event.source,
        attributes=event.details,
    )


def audit_events_to_foundry_traces(events: list[AuditEvent]) -> list[FoundryTraceRecord]:
    """Convert audit events into ordered Foundry-style traces."""

    return [audit_event_to_foundry_trace(event) for event in events]
