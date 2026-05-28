# Step 3D: Required Entities

## What We Built

We made `ready_for_simulation` smarter.

Before this step, a planned action was ready when any entity existed. Now each selected tool checks for its required entity.

## Required Entity Examples

| Tool | Required Entity |
|---|---|
| `getOrderStatus` | `order_id` |
| `validateInvoice` | `invoice_id` |
| `checkShipmentStatus` | `shipment_id` |
| `sendSupplierNotification` | `shipment_id` |
| `queryIntegrationRunStatus` | `correlation_id` |

## Example Ready Plan

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
    "ready_for_simulation": true,
    "missing_entities": []
  }
}
```

## Example Not-Ready Plan

Request:

```json
{
  "user_message": "Check order status"
}
```

Response includes:

```json
{
  "planned_action": {
    "tool_name": "getOrderStatus",
    "ready_for_simulation": false,
    "missing_entities": ["order_id"]
  }
}
```

## Why This Matters

This prevents the agent from acting on vague requests.

The agent can select a tool, but it should not proceed to execution unless required inputs are present.

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/agent_app.py` | Adds required-entity checks by tool. |
| `agent/src/api/schemas.py` | Adds `missing_entities` to planned action response. |
| `agent/src/api/routes.py` | Maps missing entities into API response. |
| `agent/tests/test_agent_flow.py` | Tests ready and not-ready planned actions. |

## Key Learning

Enterprise AI execution needs both:

1. An approved tool.
2. Complete required inputs.

Tool selection alone is not enough.

## Next Step

Step 3E can let `/agent/chat` optionally run mock simulation only when the planned action is ready and risk policy allows it.
