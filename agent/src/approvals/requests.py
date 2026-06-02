"""In-memory approval request model for high-risk planned actions."""

from dataclasses import dataclass


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


# Local approval store. Production hardening can replace this with persistent
# storage or a Logic Apps approval workflow while preserving the API shape.
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

    # Deterministic IDs make tests, demos, and audit lookups easy to follow.
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
