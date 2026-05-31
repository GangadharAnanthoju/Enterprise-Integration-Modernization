# Step 14H - Foundry Plan Uses Shared Governance

## Goal

Let Foundry mode use the same shared governance execution function as local mode.

Before this step, Foundry mode parsed the JSON plan and returned planning metadata only.

After this step, Foundry mode routes valid plans through:

```text
execute_planned_action
```

## Code Changed

```text
agent/src/foundry/agent_adapter.py
```

The Foundry adapter now:

1. invokes the live Foundry agent
2. parses the JSON action plan
3. validates selected tool and required entities
4. calls `execute_planned_action`

## Behavior

Foundry mode now matches local governance behavior:

| Scenario | Result |
|---|---|
| Ready low-risk plan, `simulate_when_ready=false` | `tool_selected` |
| Ready low-risk plan, `simulate_when_ready=true` | MCP execution |
| Missing required entity | `missing_required_entities` |
| High-risk ready plan | `approval_required` |
| Invalid JSON plan | `foundry_plan_invalid` |

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
  "correlation_id": "foundry-exec-corr-001",
  "simulate_when_ready": true
}
```

Response summary:

| Field | Value |
|---|---|
| HTTP status | `200` |
| API status | `completed` |
| Selected tool | `getOrderStatus` |
| Risk decision | `allow` |
| Tool called | `true` |
| MCP mode | `mock` |
| Request payload | `{"order_id": "ORD-1001"}` |
| Approval request | `null` |

## Why This Matters

This is the key enterprise integration milestone:

```text
Foundry reasons.
FastAPI/shared backend governance decides.
MCP executes.
Logic Apps integrates.
```

The Foundry agent is no longer only a sidecar planner. It can now feed the same governed execution path as the local adapter.

## Safety Boundary

The model still does not execute tools directly.

The model proposes:

```text
selected_tool + entities
```

Backend code decides:

```text
execute, ask for missing data, create approval, or reject
```

## Tests Updated

```text
agent/tests/test_foundry_agent_integration.py
```

Tests cover:

- plan-only Foundry behavior
- ready low-risk Foundry execution
- missing entity behavior
- high-risk approval behavior
- invalid plan rejection

## Interview Explanation

I connected the Foundry agent to the same backend governance path as the local agent. The Foundry agent returns a structured plan, but the backend still validates the selected tool, checks required entities, applies risk policy, creates approval requests, and only then executes MCP when allowed.
