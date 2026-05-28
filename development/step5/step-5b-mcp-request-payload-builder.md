# Step 5B: MCP Request Payload Builder

## What We Built

We added a validated MCP request payload builder.

The builder converts:

```text
ToolContract + extracted entities + correlation ID
```

into:

```text
McpToolRequest
```

## Example

Input:

```python
build_mcp_request(
    tool=require_tool("getOrderStatus"),
    entities={"order_id": "ORD-1001"},
    correlation_id="chat-corr-001",
)
```

Output:

```json
{
  "tool_name": "getOrderStatus",
  "correlation_id": "chat-corr-001",
  "payload": {
    "order_id": "ORD-1001"
  }
}
```

## Validation

The builder reads required entities from the tool contract:

```python
tool.required_entities
```

If required entities are missing, it raises:

```python
MissingRequiredEntitiesError
```

Example:

```text
sendSupplierNotification requires shipment_id.
entities={}
-> MissingRequiredEntitiesError(["shipment_id"])
```

## Why This Matters

This connects the agent planning layer to the MCP execution boundary.

Before this step, entities were used to decide whether a plan was ready. Now they can also become the actual request payload for MCP tools.

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/mcp/schemas.py` | Adds `McpToolRequest`. |
| `agent/src/mcp/exceptions.py` | Adds `MissingRequiredEntitiesError`. |
| `agent/src/mcp/client.py` | Adds `build_mcp_request`. |
| `agent/tests/test_mcp_request_builder.py` | Tests payload building and missing entity errors. |

## Key Learning

Planning should not directly call backend systems.

The safe handoff is:

```text
PlannedAction
  -> ToolContract validation
  -> McpToolRequest
  -> MCP execution adapter
```

## Next Step

Step 5C can make mock simulation entity-aware by using the built request payload.
