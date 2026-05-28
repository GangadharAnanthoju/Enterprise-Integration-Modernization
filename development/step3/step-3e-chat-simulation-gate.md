# Step 3E: Chat Simulation Gate

## What We Built

We let `/agent/chat` optionally run the local mock MCP simulation from the planned action.

The chat endpoint still does not execute automatically. The caller must opt in with:

```json
{
  "user_message": "Check order ORD-1001",
  "simulate_when_ready": true
}
```

## Execution Gate

Mock simulation from chat only happens when all three conditions are true:

1. The message maps to an approved MCP tool.
2. The planned action has all required entities.
3. Risk policy returns `allow`.

If any condition fails, `/agent/chat` returns the plan and explains why simulation did not run.

## Example: Allowed and Ready

Request:

```json
{
  "user_message": "Check order ORD-1001",
  "correlation_id": "chat-corr-002",
  "simulate_when_ready": true
}
```

Response includes:

```json
{
  "status": "completed",
  "tool_called": true,
  "selected_tool": "getOrderStatus",
  "simulation_result": {
    "tool_name": "getOrderStatus",
    "correlation_id": "chat-corr-002",
    "status": "completed",
    "risk_decision": "allow"
  }
}
```

## Example: Missing Required Entity

Request:

```json
{
  "user_message": "Check order status",
  "simulate_when_ready": true
}
```

Response includes:

```json
{
  "status": "missing_required_entities",
  "tool_called": false,
  "planned_action": {
    "ready_for_simulation": false,
    "missing_entities": ["order_id"]
  },
  "simulation_result": null
}
```

## Example: High Risk Still Requires Approval

Request:

```json
{
  "user_message": "Notify supplier about shipment SHIP-3001",
  "simulate_when_ready": true
}
```

Response includes:

```json
{
  "status": "approval_required",
  "tool_called": false,
  "risk_decision": "require_approval",
  "approval_required": true,
  "simulation_result": null
}
```

## Why This Matters

This is the first point where agent planning can hand off to the MCP execution boundary.

The handoff is still governed:

```text
User message
  -> planned action
  -> required entity check
  -> risk policy
  -> mock MCP simulation or approval stop
```

That keeps the project aligned with the enterprise modernization story: agents can help orchestrate work, but backend actions remain routed through governed MCP tools.

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/agent_app.py` | Adds optional chat-triggered mock simulation behind readiness and risk gates. |
| `agent/src/api/schemas.py` | Adds `simulate_when_ready` to chat requests and `simulation_result` to chat responses. |
| `agent/src/api/routes.py` | Maps optional simulation results into the public chat response. |
| `agent/tests/test_agent_flow.py` | Tests allowed simulation, missing-entity blocking, and high-risk approval blocking. |

## Key Learning

Enterprise agent execution should be explicit, gated, and auditable.

The agent can plan continuously, but it should only cross into execution when the request is specific enough and policy allows it.
