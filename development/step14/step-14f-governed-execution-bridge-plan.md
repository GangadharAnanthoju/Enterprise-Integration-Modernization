# Step 14F - Governed Execution Bridge Plan

## Goal

Define how a parsed Foundry JSON plan will move into the existing FastAPI governance and MCP execution path.

Step 14E proved this path:

```text
Foundry response
  -> parse JSON
  -> validate selected tool and required entities
  -> return PlannedAction
  -> no backend execution yet
```

Step 14F defines the next bridge:

```text
Foundry PlannedAction
  -> FastAPI governance
  -> MCP executor
  -> Logic Apps workflow
```

## Bridge Decision

Do not create a separate Foundry execution path.

Reuse the same backend enforcement path already used by the local adapter:

- approved tool lookup
- required entity validation
- risk policy
- approval request creation
- audit events
- MCP request payload builder
- MCP executor
- Logic Apps endpoint mapping

This prevents local mode and Foundry mode from drifting into two different governance systems.

## Target Flow

```text
User
  -> FastAPI /agent/chat
    -> AGENT_RUNTIME_MODE=foundry
      -> Foundry agent version 2
      -> JSON plan
      -> parse_foundry_action_plan
      -> validate_foundry_action_plan
    -> FastAPI governance bridge
      -> registry lookup
      -> risk policy
      -> approval handling
      -> MCP execution when allowed
    -> AgentChatResponse
```

## Reused Existing Behavior

The bridge should reuse the semantics already proven in local mode.

| Condition | Existing local behavior | Foundry bridge behavior |
|---|---|---|
| No selected tool | `needs_clarification` | same |
| Missing required entity | `missing_required_entities` | same |
| Ready low-risk tool, no simulation requested | `tool_selected` | same |
| Ready low-risk tool, simulation requested | execute MCP | same |
| Ready high-risk tool | create approval request | same |
| Invalid or unsupported tool | reject safely | same |

## Important Safety Rule

The model output must never directly decide execution.

The Foundry plan is only a proposal.

FastAPI must still independently decide:

```text
Can this selected tool execute now?
```

That decision must come from:

```text
agent/src/tools/registry.py
agent/src/tools/risk_policy.py
agent/src/approvals/requests.py
agent/src/mcp/client.py
```

## Proposed Code Shape

Create a shared execution function that both adapters can call.

Potential file:

```text
agent/src/agent_execution.py
```

Potential function:

```text
execute_planned_action(
    *,
    selected_tool: str | None,
    entities: dict[str, str],
    correlation_id: str,
    simulate_when_ready: bool,
    missing_entities: list[str] | None = None,
    clarification_message: str | None = None,
) -> AgentChatResult
```

The local rule-based adapter and Foundry adapter should both feed this function.

## Why A Shared Function

Right now local mode contains the mature governance flow inside:

```text
agent/src/agent_app.py
```

Foundry mode should not copy that logic.

A shared function avoids duplicated rules for:

- missing entities
- high-risk approval
- MCP execution
- response status names
- audit expectations

## Step 14G Preview

Step 14G should extract the existing local governance execution logic into a shared function while keeping all current local tests passing.

The first implementation should preserve behavior exactly.

Recommended order:

1. Extract shared function from `handle_chat_message`.
2. Keep local adapter output unchanged.
3. Add Foundry adapter tests for low-risk execution when `simulate_when_ready=true`.
4. Add Foundry adapter tests for high-risk approval behavior.
5. Run full tests.

## What Step 14F Does Not Do

This step does not execute MCP from Foundry mode yet.

It only documents the bridge design so the implementation can be small and testable.

## Interview Explanation

I did not build a second execution path for the Foundry agent. I designed the bridge so Foundry produces a structured plan, but the same FastAPI governance path still decides whether execution can happen. This keeps the model from becoming the policy engine and keeps MCP execution consistent across local and Foundry modes.
