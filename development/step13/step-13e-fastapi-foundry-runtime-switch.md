# Step 13E - FastAPI Foundry Runtime Switch

## Goal

Allow FastAPI `/agent/chat` to use either the existing local rule-based adapter or the live Foundry agent invocation path.

The default remains local so the working MCP and Logic Apps path is not changed accidentally.

## Configuration Added

```text
AGENT_RUNTIME_MODE=local
```

Supported values:

| Value | Behavior |
|---|---|
| `local` | Use the existing rule-based planner and MCP execution path |
| `foundry` | Invoke the live Foundry agent version and return the Foundry response |

## Runtime Flow

Default local mode:

```text
FastAPI /agent/chat
  -> LocalRuleBasedAgentAdapter
  -> planned action
  -> optional MCP execution when allowed
```

Foundry mode:

```text
FastAPI /agent/chat
  -> MafFoundryAgentAdapter
  -> Foundry enterprise-integration-agent:1
  -> planning response only
```

## Important Safety Boundary

In Foundry mode, `/agent/chat` does not execute Logic Apps yet.

It returns:

- status: `foundry_response`
- message: live Foundry agent text
- tool_called: `false`
- no simulation result
- no approval request

This keeps backend execution controlled while we validate the real agent response quality.

## Live Verification

The runtime switch was tested through FastAPI with:

```text
AGENT_RUNTIME_MODE=foundry
FOUNDRY_AGENT_VERSION=1
```

Request:

```json
{
  "user_message": "Check order ORD-1001",
  "correlation_id": "foundry-api-corr-001",
  "simulate_when_ready": true
}
```

Result summary:

| Field | Value |
|---|---|
| HTTP status | `200` |
| API status | `foundry_response` |
| Tool execution | `false` |
| Foundry-selected tool in message | `getOrderStatus` |
| Backend execution | not performed |

## Code Changed

| File | Change |
|---|---|
| `agent/src/config.py` | Added `agent_runtime_mode` and `foundry_agent_version` |
| `agent/src/foundry/agent_adapter.py` | Added runtime selection and live Foundry adapter path |
| `agent/src/config_validation.py` | Validates `AGENT_RUNTIME_MODE` |
| `agent/tests/test_foundry_agent_integration.py` | Tests runtime selection and no-backend-execution Foundry behavior |
| `agent/tests/test_config_validation.py` | Tests runtime mode validation |

## Why Not Execute Tools From Foundry Yet?

Tool execution needs a separate design decision:

- attach MCP tools directly to the Foundry agent
- expose tools through a dedicated MCP facade
- route Foundry planning back into FastAPI for policy enforcement

For enterprise integration, the safest next move is to keep FastAPI as the enforcement point until the tool attachment pattern is finalized.

## Interview Explanation

I added a runtime switch so the same FastAPI endpoint can call either the local planner or the live Foundry agent. Local remains the default because it already enforces MCP execution, required entities, risk policy, approval, and audit. Foundry mode is planning-only for now, which lets us test real agent behavior without bypassing backend governance.
