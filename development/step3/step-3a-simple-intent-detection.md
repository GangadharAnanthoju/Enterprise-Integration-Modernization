# Step 3A: Simple Intent Detection

## What We Built

We started the agent layer with simple, transparent intent detection.

The `/agent/chat` endpoint now looks at a user message and suggests one approved tool when the request is obvious.

## What This Is Not

This is not the real Microsoft Agent Framework integration yet.

This is a safe learning step:

- no LLM call
- no direct backend access
- no automatic tool execution
- no MCP call from chat yet

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
  "status": "tool_selected",
  "selected_tool": "getOrderStatus",
  "risk_decision": "allow",
  "approval_required": false,
  "tool_called": false
}
```

## High-Risk Example

Request:

```json
{
  "user_message": "Notify supplier about shipment delay"
}
```

Response includes:

```json
{
  "selected_tool": "sendSupplierNotification",
  "risk_decision": "require_approval",
  "approval_required": true,
  "tool_called": false
}
```

## Why `tool_called` Is Still False

The agent shell can now select a tool, but it does not execute it.

We are keeping the flow separated:

```text
User message -> intent detection -> approved tool -> risk decision
```

Execution remains in the `/tools/{tool_name}/simulate` endpoint for now.

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/agent_app.py` | Adds simple message-to-tool rules. |
| `agent/src/api/schemas.py` | Adds selected tool and risk fields to chat response. |
| `agent/src/api/routes.py` | Returns the richer chat response. |
| `agent/tests/test_agent_flow.py` | Tests low-risk, high-risk, and unmatched chat requests. |

## Key Learning

This is the first agent decision step.

We are not asking the agent to be powerful yet. We are teaching the project shape:

1. Understand user request.
2. Select only from approved tools.
3. Evaluate risk.
4. Do not execute automatically.

## Next Step

Step 3B can add extraction of simple business IDs such as order number, invoice number, and correlation ID.
