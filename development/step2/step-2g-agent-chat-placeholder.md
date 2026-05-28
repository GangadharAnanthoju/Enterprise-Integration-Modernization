# Step 2G: Agent Chat Placeholder

## What We Built

We added the first `/agent/chat` endpoint.

This is not the real AI agent yet. It is a safe placeholder that accepts a user message, creates or uses a correlation ID, and returns a controlled response.

## New API Endpoint

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/agent/chat` | Accepts a natural-language user message through the agent shell. |

## Example Request

```json
{
  "user_message": "Check order ORD-1001",
  "correlation_id": "chat-corr-001"
}
```

## Example Response

```json
{
  "correlation_id": "chat-corr-001",
  "status": "received",
  "message": "Agent shell received your request. Tool selection and Microsoft Agent Framework orchestration will be added in a later step.",
  "tool_called": false
}
```

## Why It Does Not Call Tools Yet

We are moving step by step.

Before the agent selects or executes tools, we need a stable front door:

1. Receive user message.
2. Attach correlation ID.
3. Return safe response.
4. Add tool selection later.

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/agent_app.py` | Adds the safe agent shell placeholder. |
| `agent/src/api/schemas.py` | Adds chat request and response schemas. |
| `agent/src/api/routes.py` | Adds `/agent/chat`. |
| `agent/tests/test_agent_flow.py` | Tests chat response and correlation ID behavior. |

## Key Learning

The API endpoint is the front door. The actual Microsoft Agent Framework and Foundry-specific orchestration should stay isolated in `agent_app.py` and `agent/src/foundry/`.

That keeps the rest of the API, MCP client, and risk policy stable when SDK details change.

## Next Step

Step 3A can add simple intent detection so messages like "check order" map to `getOrderStatus`, without using real AI yet.
