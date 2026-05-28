# Step 3F: Approval Request Flow

## What We Built

We added a pending approval request when `/agent/chat` receives a ready high-risk planned action and the caller asks to simulate.

The agent still does not execute the high-risk target tool. It creates an approval request that captures what would need human review.

## Example

Request:

```json
{
  "user_message": "Notify supplier about shipment SHIP-3001",
  "correlation_id": "chat-corr-003",
  "simulate_when_ready": true
}
```

Response includes:

```json
{
  "status": "approval_required",
  "tool_called": false,
  "selected_tool": "sendSupplierNotification",
  "risk_decision": "require_approval",
  "approval_required": true,
  "simulation_result": null,
  "approval_request": {
    "approval_id": "apr-chat-corr-003",
    "correlation_id": "chat-corr-003",
    "requested_tool": "sendSupplierNotification",
    "requested_entities": {
      "shipment_id": "SHIP-3001"
    },
    "status": "pending",
    "reason": "High-risk enterprise actions require human approval before execution."
  }
}
```

## Approval Gate

The approval request is only created when:

1. The user opted in with `simulate_when_ready=true`.
2. The selected tool is in the approved catalog.
3. Required entities are present.
4. Risk policy returns `require_approval`.

If required entities are missing, no approval request is created because there is not enough detail for a reviewer.

## Why This Matters

This adds the first governed human-review path.

The agent can identify a high-risk business action, package the details, and stop before execution. That is the enterprise pattern:

```text
Plan action
  -> validate required inputs
  -> evaluate risk
  -> create approval request
  -> wait for human decision
  -> execute only after approval
```

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/approvals/requests.py` | Adds the internal approval request model and factory. |
| `agent/src/approvals/__init__.py` | Marks approval helpers as a package. |
| `agent/src/agent_app.py` | Creates a pending approval request for ready high-risk planned actions. |
| `agent/src/api/schemas.py` | Adds `ApprovalRequestResponse` and exposes it from chat responses. |
| `agent/src/api/routes.py` | Maps internal approval requests to public API responses. |
| `agent/tests/test_agent_flow.py` | Tests approval request creation and confirms other paths do not create one. |

## Key Learning

High-risk actions should not disappear into a generic error.

They should become explicit, reviewable approval requests with the requested tool, business entities, correlation ID, status, and reason.

## Next Step

Step 3G can add approve/reject behavior for pending approval requests.
