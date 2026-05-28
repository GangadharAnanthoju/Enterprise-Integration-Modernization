# Step 2F: Correlation IDs

## What We Built

We added correlation IDs to mock tool simulation.

Every simulated tool call now returns a top-level `correlation_id`.

## Why This Matters

In Azure Integration Services, correlation IDs connect events across:

- API request
- Agent decision
- MCP tool call
- Logic Apps workflow run
- Azure Function helper
- Application Insights logs
- Foundry trace

We are adding this habit before connecting to Azure.

## API Behavior

If the caller sends a correlation ID, the API uses it:

```json
{
  "correlation_id": "demo-corr-001"
}
```

If the caller does not send one, the API generates a new ID.

## Example

```text
POST http://127.0.0.1:8000/tools/getOrderStatus/simulate
```

Response includes:

```json
{
  "tool_name": "getOrderStatus",
  "correlation_id": "generated-id",
  "status": "completed"
}
```

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/telemetry/correlation.py` | Generates or resolves correlation IDs. |
| `agent/src/api/schemas.py` | Adds simulation request body and correlation ID response field. |
| `agent/src/api/routes.py` | Resolves the correlation ID before simulation. |
| `agent/src/mcp/client.py` | Carries correlation ID into mock MCP simulation results. |
| `agent/tests/test_correlation.py` | Tests correlation helper behavior. |
| `agent/tests/test_agent_flow.py` | Tests correlation IDs in simulation API responses. |

## Key Learning

Correlation ID is not an AI feature. It is an integration operations feature.

The agent and Foundry will later use the same ID so troubleshooting feels familiar from your Azure Integration background.

## Next Step

Step 2G can add a basic `/agent/chat` placeholder that accepts a user message and returns a safe response without calling tools yet.
