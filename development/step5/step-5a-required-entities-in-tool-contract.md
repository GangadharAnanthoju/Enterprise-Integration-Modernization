# Step 5A: Required Entities in Tool Contract

## What We Built

We moved required entity metadata from the temporary agent planner into the governed tool catalog.

Before this step, required entities lived in `agent_app.py`:

```python
REQUIRED_ENTITIES_BY_TOOL = {
    "getOrderStatus": ("order_id",),
    ...
}
```

Now each approved MCP tool declares its own required entities:

```python
ToolContract(
    name="getOrderStatus",
    required_entities=("order_id",),
)
```

## Why This Matters

Required entities are not just agent-planning details. They are part of the tool contract.

The catalog should answer:

```text
What tool exists?
What backend does it call?
What risk level does it have?
Does it require approval?
What business entities are required before execution?
```

That makes the catalog more useful for:

```text
Future frontend forms
Foundry agent tool metadata
MCP request builders
Validation
Documentation
```

## API Change

`GET /tools` and `GET /tools/{tool_name}` now include:

```json
{
  "required_entities": ["order_id"]
}
```

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/tools/contracts.py` | Adds `required_entities` to `ToolContract`. |
| `agent/src/tools/registry.py` | Defines required entities for each approved MCP tool. |
| `agent/src/agent_app.py` | Reads missing entities from the selected tool contract. |
| `agent/src/api/schemas.py` | Exposes required entities in `ToolResponse`. |
| `agent/src/api/routes.py` | Maps contract required entities to API responses. |
| `agent/tests/test_tool_registry.py` | Tests required entity metadata in the catalog. |
| `agent/tests/test_agent_flow.py` | Tests required entities appear in the tool API. |

## Key Learning

Move stable enterprise metadata out of temporary agent logic.

The real agent can change later, but the tool contract remains the authoritative source for what an action needs before it can run.

## Next Step

Step 5B can add an MCP request payload builder that uses extracted entities and tool contract metadata.
