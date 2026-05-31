# Step 14G - Shared Governance Execution Function

## Goal

Extract the mature local governance and MCP execution behavior into a shared function.

This prepares Foundry mode to reuse the same backend enforcement path later instead of creating a second execution implementation.

## Code Added

```text
agent/src/agent_contracts.py
agent/src/agent_execution.py
```

## Contract Module

`agent_contracts.py` now owns the shared response dataclasses:

- `PlannedAction`
- `AgentChatResult`

These contracts are used by:

- local rule-based agent shell
- Foundry adapter
- FastAPI route mappers
- shared governance execution function

## Shared Execution Module

`agent_execution.py` now owns:

- `get_missing_entities`
- `execute_planned_action`

The shared function handles:

- unsupported tool rejection
- risk policy evaluation
- missing required entities
- plan-only responses
- approval request creation for high-risk tools
- MCP execution for ready allowed tools when requested

## Local Behavior

The local rule-based agent still detects tool intent and extracts entities in:

```text
agent/src/agent_app.py
```

Then it calls:

```text
execute_planned_action
```

This keeps local behavior stable while moving governance execution into a reusable boundary.

## Why This Matters

Foundry mode already returns a parsed `PlannedAction`.

The next step can route Foundry plans into the same shared execution function instead of copying governance logic into the Foundry adapter.

## Safety Boundary

This step does not yet enable MCP execution from Foundry mode.

It only creates the shared function and proves the local path still behaves correctly.

## Tests Added

```text
agent/tests/test_agent_execution.py
```

The tests cover:

- missing entity detection
- plan-only behavior
- low-risk execution when requested
- missing entity blocking
- high-risk approval request creation
- unsupported tool rejection

## Interview Explanation

I extracted governance execution into a shared backend function so policy enforcement does not depend on whether the plan came from the local rule-based shell or the live Foundry agent. This prevents drift and keeps the model out of the role of final policy authority.
