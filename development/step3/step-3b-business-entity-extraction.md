# Step 3B: Business Entity Extraction

## What We Built

We added simple extraction of business identifiers from the `/agent/chat` user message.

The endpoint can now return IDs such as:

- `order_id`
- `invoice_id`
- `shipment_id`
- `ticket_id`
- `correlation_id`

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
  "selected_tool": "getOrderStatus",
  "entities": {
    "order_id": "ORD-1001"
  }
}
```

## Why This Matters

Selecting the right tool is only half the job.

The agent also needs clean inputs to call the tool later:

```text
Check order ORD-1001
        |
        v
tool: getOrderStatus
input: order_id = ORD-1001
```

## What This Is Not

This is not full natural language understanding.

For now we use simple, transparent patterns so we can learn the flow safely before bringing in Microsoft Agent Framework and Foundry-backed model behavior.

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/agent_app.py` | Adds simple entity extraction. |
| `agent/src/api/schemas.py` | Adds `entities` to chat response. |
| `agent/src/api/routes.py` | Returns extracted entities. |
| `agent/tests/test_agent_flow.py` | Tests order, invoice, shipment, and correlation ID extraction. |

## Key Learning

The chat endpoint now returns three important things:

1. Which approved tool matched the message.
2. What risk decision applies.
3. What business identifiers were extracted.

It still does not execute tools automatically.

## Next Step

Step 3C can convert selected tools and entities into a structured planned action object.
