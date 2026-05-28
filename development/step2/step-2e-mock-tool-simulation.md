# Step 2E: Mock Tool Simulation

## What We Built

We added a local mock simulation endpoint for approved MCP tools.

This does not connect to Azure yet. It reads the sample response files under `logicapps/workflows/` so we can test the API flow safely.

## New API Endpoint

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/tools/{tool_name}/simulate` | Simulates one approved MCP tool using local sample data. |

## Example Allowed Tool

```text
POST http://127.0.0.1:8000/tools/getOrderStatus/simulate
```

Expected behavior:

- Tool exists in the catalog.
- Risk policy returns `allow`.
- API returns a sample order status response from `logicapps/workflows/getOrderStatus/sample-response.json`.

## Example High-Risk Tool

```text
POST http://127.0.0.1:8000/tools/sendSupplierNotification/simulate
```

Expected behavior:

- Tool exists in the catalog.
- Risk policy returns `require_approval`.
- API does not return the sample "sent" response.
- API returns `approval_required`.

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/mcp/client.py` | Adds local mock MCP simulation. |
| `agent/src/api/schemas.py` | Adds the simulation API response shape. |
| `agent/src/api/routes.py` | Adds `/tools/{tool_name}/simulate`. |
| `agent/tests/test_agent_flow.py` | Adds simulation tests for allowed, high-risk, and unknown tools. |

## Key Learning

Mock mode lets us build safely before Azure is connected.

The important enterprise rule is still enforced:

```text
Catalog -> Risk Policy -> Simulation
```

Even in mock mode, high-risk tools do not pretend to execute.

## Next Step

Step 2F can add request bodies and correlation IDs to simulations, so every tool call has traceability before we connect to real MCP.
