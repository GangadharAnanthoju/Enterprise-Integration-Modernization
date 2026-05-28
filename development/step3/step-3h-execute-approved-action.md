# Step 3H: Execute Approved High-Risk Action

## What We Built

We added a governed execution endpoint for approved high-risk actions.

Step 3F creates a pending approval request. Step 3G records the human decision. Step 3H executes the original high-risk MCP action only if the decision is `approved`.

## Endpoint

```text
POST /approvals/{approval_id}/execute
```

## Successful Flow

1. User asks for a high-risk action.
2. `/agent/chat` creates a pending approval request.
3. Reviewer approves the request.
4. `/approvals/{approval_id}/execute` runs the original MCP tool simulation.

Example response:

```json
{
  "approval_id": "apr-chat-corr-006",
  "approval_status": "approved",
  "execution_status": "completed",
  "tool_name": "sendSupplierNotification",
  "correlation_id": "chat-corr-006",
  "simulation_result": {
    "tool_name": "sendSupplierNotification",
    "status": "completed",
    "risk_decision": "require_approval",
    "approval_required": false
  }
}
```

## Blocked Cases

| Case | Result |
|---|---|
| Unknown approval ID | `404` |
| Approval exists but has no decision | `409` pending |
| Approval was rejected | `409` rejected |
| Approval was approved | Mock MCP simulation runs |

## Why This Matters

This completes the high-risk governance loop:

```text
Plan action
  -> risk requires approval
  -> create approval request
  -> reviewer approves
  -> execute through MCP boundary
```

The normal MCP simulation path still blocks high-risk tools. We added a separate explicit approved-execution path so the code shows why the high-risk action is allowed.

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/approvals/requests.py` | Adds lookup for recorded approval decisions. |
| `agent/src/mcp/client.py` | Adds explicit simulation after approval. |
| `agent/src/api/schemas.py` | Adds approved execution response schema. |
| `agent/src/api/routes.py` | Adds `POST /approvals/{approval_id}/execute`. |
| `agent/tests/test_agent_flow.py` | Tests approved execution and blocked pending/rejected/missing cases. |

## Key Learning

Approval should not weaken risk policy globally.

The direct simulation path still stops high-risk tools. Only the explicit approved-execution path can run them after a recorded human approval.

## Next Step

Step 4A can add persistent audit logging for plans, approvals, decisions, and executions.
