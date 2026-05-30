# Step 13D - Invoke Foundry Agent Version

## Goal

Invoke the active Foundry agent version from Python so we can prove the cloud-side agent can respond before connecting it to FastAPI.

## Code Added

```text
agent/src/foundry/live_agent.py
```

New invocation helpers:

| Function or class | Purpose |
|---|---|
| `create_foundry_runtime_agent` | Creates a `FoundryAgent` runtime client with Azure CLI credentials |
| `invoke_foundry_agent_message_async` | Invokes the configured Foundry agent with one user message |
| `invoke_foundry_agent_message` | Synchronous wrapper for scripts and demos |
| `FoundryAgentInvocationResult` | Safe response summary for invocation results |

## Configuration Added

```text
FOUNDRY_AGENT_VERSION=1
```

The version is optional in code, but setting it makes local testing explicit and repeatable.

## Invocation Path

```text
Python helper
  -> FoundryAgent runtime client
  -> Foundry project endpoint
  -> enterprise-integration-agent:1
  -> gpt-4.1-mini model deployment
```

## What This Proves

This step proves:

- the Foundry project endpoint is usable
- Azure CLI identity can reach the project
- the agent version is active enough to receive a prompt
- the checked-in instruction file can guide the agent response

## Live Invocation Result

Test message:

```text
Check order ORD-1001
```

Live result summary:

| Field | Value |
|---|---|
| Agent | `enterprise-integration-agent` |
| Version | `1` |
| Response ID | `resp_0601a1fae2abb536006a1b02a2427c819097ecd9ee8023202d` |
| Selected tool in response | `getOrderStatus` |
| Required entity in response | `order_id = ORD-1001` |
| Execution posture | ready for execution, asks before proceeding |

This is the right behavior for this phase. The Foundry agent can reason over the request and select the approved tool, but it does not execute Logic Apps yet because MCP tool attachment is not part of Step 13D.

## What This Does Not Do Yet

- It does not attach live MCP tools inside Foundry.
- It does not execute Logic Apps from the Foundry agent.
- It does not replace the FastAPI `/agent/chat` path.
- It does not publish the agent as an Agent Application.

Those belong to later steps.

## Test Strategy

Unit tests use a fake runtime agent so normal test runs do not call Azure.

The live invocation should be run manually only when:

- `agent/.env` has the Foundry endpoint and model deployment
- Azure CLI is logged in
- the user is ready for a live Foundry call

## Interview Explanation

Step 13D moves from agent creation to agent invocation. I added a small Foundry runtime boundary that can send one message to the active agent version and return a safe summary. The unit tests fake the runtime client, so CI and local tests stay offline. The live call is still controlled and separate from FastAPI until we are ready to switch the adapter.
