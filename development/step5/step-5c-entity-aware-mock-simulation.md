# Step 5C: Entity-Aware Mock Simulation

## What We Built

We made mock MCP simulation carry the validated request payload.

Before this step, simulation returned only a sample response.

Now, when the agent has extracted entities, simulation also returns:

```json
{
  "request_payload": {
    "order_id": "ORD-1001"
  }
}
```

## Why This Matters

This makes the mock path look more like real MCP execution.

The flow is now:

```text
User message
  -> extracted entities
  -> ToolContract.required_entities validation
  -> McpToolRequest
  -> mock MCP simulation
  -> simulation result includes request payload
```

## Examples

Order status:

```json
{
  "tool_name": "getOrderStatus",
  "request_payload": {
    "order_id": "ORD-1001"
  },
  "result": {
    "orderNumber": "4500098123"
  }
}
```

Approved supplier notification:

```json
{
  "tool_name": "sendSupplierNotification",
  "request_payload": {
    "shipment_id": "SHIP-3004"
  },
  "risk_decision": "require_approval",
  "approval_required": false
}
```

## Important Governance Detail

The normal direct simulation path still blocks high-risk tools.

The approved execution path can include a high-risk request payload only after:

```text
approval request exists
approval decision exists
decision == approved
```

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/mcp/client.py` | Simulation functions now optionally build and carry `McpToolRequest`. |
| `agent/src/api/schemas.py` | Adds `request_payload` to `ToolSimulationResponse`. |
| `agent/src/api/routes.py` | Maps simulation request payloads to API responses. |
| `agent/src/agent_app.py` | Passes extracted entities into MCP simulation. |
| `agent/tests/test_agent_flow.py` | Tests request payloads in chat and approved execution responses. |
| `agent/tests/test_mcp_request_builder.py` | Tests simulation request payload behavior. |

## Key Learning

Mock simulation should still respect the real execution contract.

Even without Azure connectivity, we can prove the agent is preparing the correct MCP request shape.

## Next Step

Step 5D can add MCP server configuration placeholders for the future Logic Apps Standard MCP connection.
