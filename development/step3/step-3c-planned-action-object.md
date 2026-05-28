# Step 3C: Planned Action Object

## What We Built

We added a structured `planned_action` object to `/agent/chat`.

This object packages the selected tool, extracted entities, and risk decision into one place before any tool execution happens.

## Example

Request:

```json
{
  "user_message": "Check order ORD-1001"
}
```

Response includes:

```json
{
  "planned_action": {
    "tool_name": "getOrderStatus",
    "entities": {
      "order_id": "ORD-1001"
    },
    "risk_decision": "allow",
    "approval_required": false,
    "ready_for_simulation": true
  }
}
```

## Why This Matters

This creates a clean handoff between agent planning and tool execution.

Later, Microsoft Agent Framework and Foundry can produce the same shape:

```text
User message
  -> agent reasoning
  -> planned action
  -> risk policy
  -> approval or MCP execution
```

## Still No Execution

`/agent/chat` still does not call MCP tools.

It only creates a plan.

Execution stays in:

```text
POST /tools/{tool_name}/simulate
```

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/agent_app.py` | Adds the internal `PlannedAction` model. |
| `agent/src/api/schemas.py` | Adds the API `PlannedActionResponse` model. |
| `agent/src/api/routes.py` | Maps internal planned action to API response. |
| `agent/tests/test_agent_flow.py` | Tests planned action for normal, high-risk, and unmatched requests. |

## Key Learning

Planning and execution should be separate.

That separation is one of the most important enterprise AI safety patterns in this project.

## Next Step

Step 3D can add an explicit `ready_for_simulation` rule that checks whether required entities are present for each selected tool.
