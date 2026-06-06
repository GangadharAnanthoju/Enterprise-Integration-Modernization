"""Approval request model for high-risk planned actions."""

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ApprovalRequest:
    """Approval task created when a high-risk action is ready but blocked."""

    approval_id: str
    correlation_id: str
    requested_tool: str
    requested_entities: dict[str, str]
    status: str
    reason: str


@dataclass(frozen=True)
class ApprovalDecision:
    """Human decision recorded for a pending approval request."""

    approval_id: str
    correlation_id: str
    requested_tool: str
    decision: str
    status: str
    reviewer: str
    comment: str | None


class ApprovalRepository(Protocol):
    """Storage boundary for approval requests and decisions."""

    def create_request(
        self,
        *,
        correlation_id: str,
        requested_tool: str,
        requested_entities: dict[str, str],
        reason: str,
    ) -> ApprovalRequest:
        """Create a pending approval request."""

    def get_request(self, approval_id: str) -> ApprovalRequest | None:
        """Return one approval request by ID."""

    def get_decision(self, approval_id: str) -> ApprovalDecision | None:
        """Return one approval decision by approval ID."""

    def decide_request(
        self,
        *,
        approval_id: str,
        decision: str,
        reviewer: str,
        comment: str | None,
    ) -> ApprovalDecision | None:
        """Record a human decision for an existing approval request."""

    def is_available(self) -> bool:
        """Return whether the approval store is available."""


class InMemoryApprovalRepository:
    """In-memory approval repository for local development and tests."""

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}
        self._decisions: dict[str, ApprovalDecision] = {}

    @property
    def requests(self) -> dict[str, ApprovalRequest]:
        """Return the mutable request store for compatibility checks."""

        return self._requests

    @property
    def decisions(self) -> dict[str, ApprovalDecision]:
        """Return the mutable decision store for compatibility checks."""

        return self._decisions

    def create_request(
        self,
        *,
        correlation_id: str,
        requested_tool: str,
        requested_entities: dict[str, str],
        reason: str,
    ) -> ApprovalRequest:
        """Create a pending approval request for a blocked high-risk action."""

        # Deterministic IDs make tests, demos, and audit lookups easy to follow.
        approval_request = ApprovalRequest(
            approval_id=f"apr-{correlation_id}",
            correlation_id=correlation_id,
            requested_tool=requested_tool,
            requested_entities=requested_entities,
            status="pending",
            reason=reason,
        )
        self._requests[approval_request.approval_id] = approval_request
        return approval_request

    def get_request(self, approval_id: str) -> ApprovalRequest | None:
        """Return one approval request by ID."""

        return self._requests.get(approval_id)

    def get_decision(self, approval_id: str) -> ApprovalDecision | None:
        """Return the recorded decision for one approval request."""

        return self._decisions.get(approval_id)

    def decide_request(
        self,
        *,
        approval_id: str,
        decision: str,
        reviewer: str,
        comment: str | None,
    ) -> ApprovalDecision | None:
        """Record an approve/reject decision for an existing approval request."""

        approval_request = self.get_request(approval_id)
        if approval_request is None:
            return None

        approval_decision = ApprovalDecision(
            approval_id=approval_request.approval_id,
            correlation_id=approval_request.correlation_id,
            requested_tool=approval_request.requested_tool,
            decision=decision,
            status=decision,
            reviewer=reviewer,
            comment=comment,
        )
        self._decisions[approval_id] = approval_decision
        return approval_decision

    def is_available(self) -> bool:
        """Return whether the in-memory approval store is available."""

        return isinstance(self._requests, dict) and isinstance(self._decisions, dict)


class AzureTableApprovalRepository:
    """Durable approval repository backed by Azure Table Storage."""

    def __init__(self, requests_table_client: Any, decisions_table_client: Any) -> None:
        self._requests_table_client = requests_table_client
        self._decisions_table_client = decisions_table_client

    def create_request(
        self,
        *,
        correlation_id: str,
        requested_tool: str,
        requested_entities: dict[str, str],
        reason: str,
    ) -> ApprovalRequest:
        """Create or replace a pending approval request."""

        request = ApprovalRequest(
            approval_id=f"apr-{correlation_id}",
            correlation_id=correlation_id,
            requested_tool=requested_tool,
            requested_entities=requested_entities,
            status="pending",
            reason=reason,
        )
        self._requests_table_client.upsert_entity(
            {
                "PartitionKey": "approval_request",
                "RowKey": _table_key(request.approval_id),
                "approval_id": request.approval_id,
                "correlation_id": request.correlation_id,
                "requested_tool": request.requested_tool,
                "requested_entities_json": json.dumps(
                    request.requested_entities, separators=(",", ":")
                ),
                "status": request.status,
                "reason": request.reason,
            }
        )
        return request

    def get_request(self, approval_id: str) -> ApprovalRequest | None:
        """Return one approval request by ID."""

        try:
            entity = self._requests_table_client.get_entity(
                partition_key="approval_request",
                row_key=_table_key(approval_id),
            )
        except Exception as exc:
            if _is_entity_not_found(exc):
                return None
            raise
        return ApprovalRequest(
            approval_id=str(entity["approval_id"]),
            correlation_id=str(entity["correlation_id"]),
            requested_tool=str(entity["requested_tool"]),
            requested_entities=json.loads(str(entity["requested_entities_json"])),
            status=str(entity["status"]),
            reason=str(entity["reason"]),
        )

    def get_decision(self, approval_id: str) -> ApprovalDecision | None:
        """Return one approval decision by approval ID."""

        try:
            entity = self._decisions_table_client.get_entity(
                partition_key="approval_decision",
                row_key=_table_key(approval_id),
            )
        except Exception as exc:
            if _is_entity_not_found(exc):
                return None
            raise
        return ApprovalDecision(
            approval_id=str(entity["approval_id"]),
            correlation_id=str(entity["correlation_id"]),
            requested_tool=str(entity["requested_tool"]),
            decision=str(entity["decision"]),
            status=str(entity["status"]),
            reviewer=str(entity["reviewer"]),
            comment=str(entity["comment"]) if entity.get("comment") is not None else None,
        )

    def decide_request(
        self,
        *,
        approval_id: str,
        decision: str,
        reviewer: str,
        comment: str | None,
    ) -> ApprovalDecision | None:
        """Record an approve/reject decision for an existing approval request."""

        request = self.get_request(approval_id)
        if request is None:
            return None
        approval_decision = ApprovalDecision(
            approval_id=request.approval_id,
            correlation_id=request.correlation_id,
            requested_tool=request.requested_tool,
            decision=decision,
            status=decision,
            reviewer=reviewer,
            comment=comment,
        )
        entity = {
            "PartitionKey": "approval_decision",
            "RowKey": _table_key(approval_id),
            "approval_id": approval_decision.approval_id,
            "correlation_id": approval_decision.correlation_id,
            "requested_tool": approval_decision.requested_tool,
            "decision": approval_decision.decision,
            "status": approval_decision.status,
            "reviewer": approval_decision.reviewer,
        }
        if approval_decision.comment is not None:
            entity["comment"] = approval_decision.comment
        self._decisions_table_client.upsert_entity(entity)
        return approval_decision

    def is_available(self) -> bool:
        """Return whether both Azure Table clients were configured."""

        return self._requests_table_client is not None and self._decisions_table_client is not None


def _table_key(value: str) -> str:
    """Return a deterministic Azure Table-safe key."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _is_entity_not_found(exc: Exception) -> bool:
    """Return whether an Azure SDK exception represents a missing entity."""

    return exc.__class__.__name__ == "ResourceNotFoundError"


_IN_MEMORY_APPROVAL_REPOSITORY = InMemoryApprovalRepository()
APPROVAL_REPOSITORY: ApprovalRepository = _IN_MEMORY_APPROVAL_REPOSITORY
APPROVAL_REQUESTS = _IN_MEMORY_APPROVAL_REPOSITORY.requests
APPROVAL_DECISIONS = _IN_MEMORY_APPROVAL_REPOSITORY.decisions


def create_approval_request(
    *,
    correlation_id: str,
    requested_tool: str,
    requested_entities: dict[str, str],
    reason: str,
) -> ApprovalRequest:
    """Create a pending approval request for a blocked high-risk action."""

    return APPROVAL_REPOSITORY.create_request(
        correlation_id=correlation_id,
        requested_tool=requested_tool,
        requested_entities=requested_entities,
        reason=reason,
    )


def get_approval_request(approval_id: str) -> ApprovalRequest | None:
    """Return one pending approval request by ID."""

    return APPROVAL_REPOSITORY.get_request(approval_id)


def get_approval_decision(approval_id: str) -> ApprovalDecision | None:
    """Return the recorded decision for one approval request."""

    return APPROVAL_REPOSITORY.get_decision(approval_id)


def decide_approval_request(
    *,
    approval_id: str,
    decision: str,
    reviewer: str,
    comment: str | None,
) -> ApprovalDecision | None:
    """Record an approve/reject decision for an existing approval request."""

    return APPROVAL_REPOSITORY.decide_request(
        approval_id=approval_id,
        decision=decision,
        reviewer=reviewer,
        comment=comment,
    )


def get_approval_repository() -> ApprovalRepository:
    """Return the configured approval repository."""

    return APPROVAL_REPOSITORY


def set_approval_repository(repository: ApprovalRepository) -> None:
    """Set the approval repository used by application-level helper functions."""

    global APPROVAL_REPOSITORY
    APPROVAL_REPOSITORY = repository
