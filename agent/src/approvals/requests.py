"""In-memory approval request model for high-risk planned actions."""

from dataclasses import dataclass


# **************** TEMPORARY APPROVAL STORE ****************
# These approval classes are active now, but they are intentionally lightweight.
# Later they should move behind a real approval workflow, database, or Logic
# Apps-backed approval service while preserving the API response shape.
# *******************************************************


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


# TEMPORARY STORAGE: dictionaries keep approvals available across requests
# during local development. Replace this with persistent storage later.
APPROVAL_REQUESTS: dict[str, ApprovalRequest] = {}
APPROVAL_DECISIONS: dict[str, ApprovalDecision] = {}


def create_approval_request(
    *,
    correlation_id: str,
    requested_tool: str,
    requested_entities: dict[str, str],
    reason: str,
) -> ApprovalRequest:
    """Create a pending approval request for a blocked high-risk action."""

    # This is in-memory and deterministic for now so tests and demos can make
    # clear assertions. A later step can persist approvals in a database or
    # call a real approval workflow service.
    approval_request = ApprovalRequest(
        approval_id=f"apr-{correlation_id}",
        correlation_id=correlation_id,
        requested_tool=requested_tool,
        requested_entities=requested_entities,
        status="pending",
        reason=reason,
    )
    APPROVAL_REQUESTS[approval_request.approval_id] = approval_request
    return approval_request


def get_approval_request(approval_id: str) -> ApprovalRequest | None:
    """Return one pending approval request by ID."""

    return APPROVAL_REQUESTS.get(approval_id)


def get_approval_decision(approval_id: str) -> ApprovalDecision | None:
    """Return the recorded decision for one approval request."""

    return APPROVAL_DECISIONS.get(approval_id)


def decide_approval_request(
    *,
    approval_id: str,
    decision: str,
    reviewer: str,
    comment: str | None,
) -> ApprovalDecision | None:
    """Record an approve/reject decision for an existing approval request."""

    approval_request = get_approval_request(approval_id)
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
    APPROVAL_DECISIONS[approval_id] = approval_decision
    return approval_decision
