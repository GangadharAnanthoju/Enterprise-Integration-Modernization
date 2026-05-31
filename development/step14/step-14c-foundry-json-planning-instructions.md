# Step 14C - Foundry JSON Planning Instructions

## Goal

Update the Foundry agent instructions so the live agent returns the structured plan format defined in Step 14B.

## Instruction Change

The instruction file now tells the agent:

```text
When asked to plan an enterprise integration action, return only one JSON object.
```

The required shape is:

```json
{
  "selected_tool": "getOrderStatus",
  "entities": {
    "order_id": "ORD-1001"
  },
  "requires_clarification": false,
  "clarification_question": null,
  "confidence": "high",
  "reason": "The user asked to check the status of order ORD-1001."
}
```

## Why This Matters

Step 13 proved the live Foundry agent can respond, but the response was human-readable text.

Human-readable text is useful for demos, but backend governance needs a deterministic contract.

The structured JSON plan lets FastAPI:

- parse the selected tool
- validate the tool against the registry
- check required entities
- reject unsupported tool names
- decide whether to ask for clarification
- apply risk policy later

## Safety Rule

The updated instructions explicitly say:

```text
Do not claim that a backend workflow was executed.
```

This keeps Foundry in planning mode until later steps connect structured plans to governed MCP execution.

## Tests Updated

```text
agent/tests/test_foundry_agent_instructions.py
```

The tests now check that the instruction file includes:

- JSON-only planning guidance
- required plan fields
- no false backend execution claim
- current approved tool names

## What Is Not Done Yet

This step does not create a new Foundry agent version.

The live Foundry project still has the previous version until we explicitly run the registration helper again.

## Next Step

Step 14D should create a new Foundry agent version with the updated JSON planning instructions and verify the live response can be parsed by:

```text
parse_foundry_action_plan
```
