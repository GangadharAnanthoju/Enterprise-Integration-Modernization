# Step 3G: Approval Decision

## What We Built

We added an approval decision API for pending high-risk action requests.

Step 3F created the pending approval request. Step 3G lets a human reviewer approve or reject it.

## Endpoint

```text
POST /approvals/{approval_id}/decision
```

Request:

```json
{
  "decision": "approved",
  "reviewer": "integration.manager@contoso.com",
  "comment": "Supplier notification is valid."
}
```

Response:

```json
{
  "approval_id": "apr-chat-corr-004",
  "correlation_id": "chat-corr-004",
  "requested_tool": "sendSupplierNotification",
  "decision": "approved",
  "status": "approved",
  "reviewer": "integration.manager@contoso.com",
  "comment": "Supplier notification is valid."
}
```

## Rejection Example

Request:

```json
{
  "decision": "rejected",
  "reviewer": "integration.manager@contoso.com",
  "comment": "Need more business context."
}
```

Response includes:

```json
{
  "decision": "rejected",
  "status": "rejected"
}
```

## Why This Matters

This separates human approval from backend execution.

The workflow is now:

```text
Agent detects high-risk action
  -> creates pending approval request
  -> reviewer approves or rejects
  -> execution still waits for the next governed step
```

That separation matters in enterprise systems because approval is a business decision, and execution is an integration action.

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/approvals/requests.py` | Stores pending approval requests and records approval decisions in memory. |
| `agent/src/api/schemas.py` | Adds approval decision request and response schemas. |
| `agent/src/api/routes.py` | Adds `POST /approvals/{approval_id}/decision`. |
| `agent/tests/test_agent_flow.py` | Tests approved, rejected, and unknown approval decision cases. |

## Key Learning

Do not immediately execute a high-risk action just because someone approved it.

Approval should create a clear state transition first. A later execution step can verify that state before calling MCP.

## Next Step

Step 3H can execute an approved high-risk action through MCP simulation.
