# Step 14E - Foundry Adapter Parses JSON Plan

## Goal

Connect the Foundry runtime adapter to the structured JSON plan parser from Step 14B.

Before this step, `AGENT_RUNTIME_MODE=foundry` returned raw Foundry text. After this step, the adapter parses the Foundry response and maps it into the existing FastAPI planning response shape.

## Code Changed

```text
agent/src/foundry/agent_adapter.py
```

The `MafFoundryAgentAdapter` now:

1. invokes the live Foundry agent
2. parses the JSON response with `parse_foundry_action_plan`
3. validates the plan with `validate_foundry_action_plan`
4. evaluates risk policy for the selected tool
5. returns an `AgentChatResult` with a populated `PlannedAction`

## Runtime Behavior

Ready low-risk plan:

```text
status=foundry_plan_ready
selected_tool=getOrderStatus
entities={"order_id": "ORD-1001"}
tool_called=false
simulation_result=null
```

Missing entity plan:

```text
status=missing_required_entities
selected_tool=getOrderStatus
missing_entities=["order_id"]
tool_called=false
simulation_result=null
```

Invalid Foundry response:

```text
status=foundry_plan_invalid
tool_called=false
planned_action=null
simulation_result=null
```

## Live Verification

The FastAPI path was verified with:

```text
AGENT_RUNTIME_MODE=foundry
FOUNDRY_AGENT_VERSION=2
```

Request:

```json
{
  "user_message": "Check order ORD-1001",
  "correlation_id": "foundry-json-corr-001",
  "simulate_when_ready": true
}
```

Response summary:

| Field | Value |
|---|---|
| HTTP status | `200` |
| API status | `foundry_plan_ready` |
| Selected tool | `getOrderStatus` |
| Risk decision | `allow` |
| Approval required | `false` |
| Entities | `{"order_id": "ORD-1001"}` |
| Ready for simulation | `true` |
| Tool called | `false` |
| Simulation result | `null` |

## Safety Boundary

This step still does not execute MCP or Logic Apps from Foundry mode.

Even if the Foundry plan is valid and `simulate_when_ready=true`, the adapter returns a validated plan only.

Execution remains disabled until a later step connects the parsed Foundry plan to the same FastAPI governance execution path used by the local adapter.

## Tests Updated

```text
agent/tests/test_foundry_agent_integration.py
agent/tests/test_maf_agent_skeleton.py
```

The tests verify:

- Foundry runtime mode reports structured planning
- valid JSON plans populate `PlannedAction`
- missing entities are exposed in the API planning shape
- invalid Foundry text is rejected safely
- no backend execution happens in Foundry mode

## Interview Explanation

I connected the live Foundry agent to a structured plan parser, but I still did not let it execute tools. The adapter now turns model output into the same internal planning object used by FastAPI. That lets the backend apply deterministic governance before any future MCP or Logic Apps call.
