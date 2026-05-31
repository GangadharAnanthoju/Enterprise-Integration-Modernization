# Step 14D - Live Foundry JSON Plan Verification

## Goal

Create a new Foundry agent version with the updated JSON planning instructions and verify the live response can be parsed by the Step 14B planning contract.

## Live Foundry Version Created

| Field | Value |
|---|---|
| Agent | `enterprise-integration-agent` |
| New version | `2` |
| Status | `active` |
| Prompt source | `agent/src/prompts/foundry_agent_instructions.md` |
| Model deployment | `gpt-4.1-mini` |

## Test Prompt

```text
Check order ORD-1001
```

## Live Response

The live Foundry agent returned fenced JSON:

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

## Parser Result

The response was parsed by:

```text
parse_foundry_action_plan
```

Validation result:

| Field | Value |
|---|---|
| Parsed tool | `getOrderStatus` |
| Parsed entities | `{"order_id": "ORD-1001"}` |
| Requires clarification | `false` |
| Confidence | `high` |
| Ready for governance | `true` |
| Missing entities | `[]` |

## What This Proves

This proves the live Foundry agent can now produce a machine-readable plan that backend code can validate before execution.

We are no longer depending on free-form text like:

```text
Selected tool: getOrderStatus
```

Instead, the next step can use structured data:

```text
Foundry JSON plan
  -> parse
  -> validate against registry
  -> enforce risk policy
  -> execute MCP only when allowed
```

## What Is Still Not Done

This step still does not execute Logic Apps from Foundry.

Backend execution remains intentionally disabled until FastAPI validates the structured plan through the same governance path as the local adapter.

## Next Step

Step 14E should connect the Foundry adapter to this parser.

Expected behavior in `AGENT_RUNTIME_MODE=foundry`:

```text
Foundry response text
  -> parse_foundry_action_plan
  -> validate_foundry_action_plan
  -> return parsed plan metadata in /agent/chat
```

Execution should still remain disabled until a later step.

## Interview Explanation

After updating the Foundry instructions, I created a new Foundry agent version and verified that the live agent returned a valid JSON plan. I parsed that response with backend code and validated it against the approved tool registry. This proves the project can move from natural-language model output to deterministic governance enforcement.
