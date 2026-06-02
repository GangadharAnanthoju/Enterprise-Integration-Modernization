"""In-memory audit events for agent planning, approvals, and executions."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    """One auditable state transition in the governed agent workflow."""

    event_id: str
    correlation_id: str
    event_type: str
    source: str
    status: str
    details: dict[str, Any]


# Local audit store used by the API and tests. Production hardening can swap
# this behind the same functions for durable storage and Azure Monitor export.
AUDIT_EVENTS: list[AuditEvent] = []


def record_audit_event(
    *,
    correlation_id: str,
    event_type: str,
    source: str,
    status: str,
    details: dict[str, Any],
) -> AuditEvent:
    """Record one audit event and return it."""

    audit_event = AuditEvent(
        event_id=f"audit-{len(AUDIT_EVENTS) + 1:04d}",
        correlation_id=correlation_id,
        event_type=event_type,
        source=source,
        status=status,
        details=details,
    )
    AUDIT_EVENTS.append(audit_event)
    return audit_event


def list_audit_events(correlation_id: str) -> list[AuditEvent]:
    """Return audit events for one correlation ID in write order."""

    return [event for event in AUDIT_EVENTS if event.correlation_id == correlation_id]
