"""Audit events for agent planning, approvals, and executions."""

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4


@dataclass(frozen=True)
class AuditEvent:
    """One auditable state transition in the governed agent workflow."""

    event_id: str
    correlation_id: str
    event_type: str
    source: str
    status: str
    details: dict[str, Any]


class AuditRepository(Protocol):
    """Storage boundary for audit events."""

    def record(
        self,
        *,
        correlation_id: str,
        event_type: str,
        source: str,
        status: str,
        details: dict[str, Any],
    ) -> AuditEvent:
        """Record one audit event."""

    def list_by_correlation_id(self, correlation_id: str) -> list[AuditEvent]:
        """Return audit events for one correlation ID."""

    def is_available(self) -> bool:
        """Return whether the audit store is available."""


class InMemoryAuditRepository:
    """In-memory audit repository for local development and tests."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    @property
    def events(self) -> list[AuditEvent]:
        """Return the mutable backing list for compatibility with existing checks."""

        return self._events

    def record(
        self,
        *,
        correlation_id: str,
        event_type: str,
        source: str,
        status: str,
        details: dict[str, Any],
    ) -> AuditEvent:
        """Record one audit event and return it."""

        audit_event = AuditEvent(
            event_id=f"audit-{len(self._events) + 1:04d}",
            correlation_id=correlation_id,
            event_type=event_type,
            source=source,
            status=status,
            details=details,
        )
        self._events.append(audit_event)
        return audit_event

    def list_by_correlation_id(self, correlation_id: str) -> list[AuditEvent]:
        """Return audit events for one correlation ID in write order."""

        return [event for event in self._events if event.correlation_id == correlation_id]

    def is_available(self) -> bool:
        """Return whether the in-memory store is available."""

        return isinstance(self._events, list)


class AzureTableAuditRepository:
    """Durable audit repository backed by Azure Table Storage."""

    def __init__(self, table_client: Any) -> None:
        self._table_client = table_client

    def record(
        self,
        *,
        correlation_id: str,
        event_type: str,
        source: str,
        status: str,
        details: dict[str, Any],
    ) -> AuditEvent:
        """Record one audit event in Azure Table Storage."""

        event_id = f"audit-{uuid4()}"
        created_at = datetime.now(UTC).isoformat()
        event = AuditEvent(
            event_id=event_id,
            correlation_id=correlation_id,
            event_type=event_type,
            source=source,
            status=status,
            details=details,
        )
        self._table_client.create_entity(
            {
                "PartitionKey": _table_key(correlation_id),
                "RowKey": f"{created_at}-{event_id}",
                "event_id": event.event_id,
                "correlation_id": event.correlation_id,
                "event_type": event.event_type,
                "source": event.source,
                "status": event.status,
                "details_json": json.dumps(event.details, separators=(",", ":")),
                "created_at": created_at,
            }
        )
        return event

    def list_by_correlation_id(self, correlation_id: str) -> list[AuditEvent]:
        """Return audit events for one correlation ID in write order."""

        entities = self._table_client.query_entities(
            query_filter=f"PartitionKey eq '{_table_key(correlation_id)}'"
        )
        ordered_entities = sorted(entities, key=lambda entity: str(entity["created_at"]))
        return [
            AuditEvent(
                event_id=str(entity["event_id"]),
                correlation_id=str(entity["correlation_id"]),
                event_type=str(entity["event_type"]),
                source=str(entity["source"]),
                status=str(entity["status"]),
                details=json.loads(str(entity["details_json"])),
            )
            for entity in ordered_entities
        ]

    def is_available(self) -> bool:
        """Return whether the Azure Table client was configured."""

        return self._table_client is not None


def _table_key(value: str) -> str:
    """Return a deterministic Azure Table-safe key."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


_IN_MEMORY_AUDIT_REPOSITORY = InMemoryAuditRepository()
AUDIT_REPOSITORY: AuditRepository = _IN_MEMORY_AUDIT_REPOSITORY
AUDIT_EVENTS = _IN_MEMORY_AUDIT_REPOSITORY.events


def record_audit_event(
    *,
    correlation_id: str,
    event_type: str,
    source: str,
    status: str,
    details: dict[str, Any],
) -> AuditEvent:
    """Record one audit event and return it."""

    event = AUDIT_REPOSITORY.record(
        correlation_id=correlation_id,
        event_type=event_type,
        source=source,
        status=status,
        details=details,
    )
    from telemetry.exporter import emit_audit_event

    emit_audit_event(event)
    return event


def list_audit_events(correlation_id: str) -> list[AuditEvent]:
    """Return audit events for one correlation ID in write order."""

    return AUDIT_REPOSITORY.list_by_correlation_id(correlation_id)


def get_audit_repository() -> AuditRepository:
    """Return the configured audit repository."""

    return AUDIT_REPOSITORY


def set_audit_repository(repository: AuditRepository) -> None:
    """Set the audit repository used by application-level helper functions."""

    global AUDIT_REPOSITORY
    AUDIT_REPOSITORY = repository
