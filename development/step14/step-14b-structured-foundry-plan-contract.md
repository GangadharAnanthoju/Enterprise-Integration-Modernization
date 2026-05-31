# Step 14B - Structured Foundry Plan Contract

## Goal

Add a code-level contract for the structured plan that the Foundry agent should return.

Step 14A decided the strategy:

```text
Foundry reasons.
FastAPI governs.
MCP executes.
Logic Apps integrates.
```

Step 14B creates the first deterministic object for the "Foundry reasons" part.

## Code Added

```text
agent/src/foundry/planning.py
```

It defines:

| Type or function | Purpose |
|---|---|
| `FoundryActionPlan` | Structured plan proposed by the Foundry agent |
| `FoundryPlanValidation` | Registry validation result for the plan |
| `FoundryPlanContractError` | Clear failure when Foundry returns invalid plan JSON |
| `parse_foundry_action_plan` | Parses JSON or fenced JSON from a Foundry response |
| `validate_foundry_action_plan` | Checks selected tool and missing required entities |

## Plan Shape

The target Foundry response is:

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

## Validation Rules

The parser checks:

- response contains a JSON object
- required fields are present
- `selected_tool` is either `null` or an approved tool
- `entities` is an object with string keys and values
- `requires_clarification` is a boolean
- `confidence` is `low`, `medium`, or `high`
- `reason` is not empty
- clarification requests include a clarification question

The registry validator checks:

- whether the selected tool is supported
- which required entities are missing
- whether the plan is ready for later governance enforcement

## What This Does Not Do Yet

This step does not:

- change the live Foundry prompt
- require the live Foundry agent to emit JSON yet
- execute MCP tools from Foundry plans
- change `/agent/chat` behavior

Those belong to later steps.

## Why This Matters

Free-form model text is useful for humans, but backend execution needs a stable contract.

This contract lets the next steps safely convert a Foundry response into something FastAPI can validate using deterministic code.

## Tests Added

```text
agent/tests/test_foundry_planning.py
```

The tests cover:

- valid JSON plans
- fenced JSON plans
- unsupported tool rejection
- missing clarification question rejection
- missing required entity detection
- ready plan detection
- unsupported request clarification

## Interview Explanation

I did not let the live agent's free-form text drive backend execution. I added a structured plan contract first. The plan can select a tool and extract entities, but backend code still validates the selected tool against the registry and checks required entities before any MCP execution can happen.
