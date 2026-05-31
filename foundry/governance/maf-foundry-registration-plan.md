# MAF And Foundry Registration Plan

This plan describes how the enterprise integration agent should be registered in Microsoft Foundry using Microsoft Agent Framework.

This is not the publishing step. Publishing happens later, after the agent is created, tested, and evaluated.

## Registration Inputs

| Field | Value |
|---|---|
| Agent name | `enterprise-integration-agent` |
| Display name | `Enterprise Integration Modernization Agent` |
| Framework | `microsoft_agent_framework` |
| Target runtime | `microsoft_foundry` |
| Project endpoint | `FOUNDRY_PROJECT_ENDPOINT` |
| Model deployment | `MODEL_DEPLOYMENT_NAME` |
| Instruction source | `agent/src/prompts/foundry_agent_instructions.md` |
| Tool metadata source | `agent/src/foundry/tool_registration.py` |
| FastAPI boundary | `/agent/chat` |
| Publish immediately | `false` |

## Intended Creation Flow

```text
Local MAF agent skeleton
  -> register/create Foundry agent in project
  -> test inside Foundry project
  -> attach approved MCP tool layer
  -> run evaluations
  -> publish later as Agent Application
```

## Why MAF Comes Before Publishing

Microsoft Agent Framework is the agent implementation path.

Microsoft Foundry is the runtime, governance, evaluation, and publishing platform.

Publishing should not happen until the agent has:

- stable instructions
- correct model deployment
- approved tool metadata
- evaluated behavior
- clear RBAC and invocation plan

## Tool Strategy

The first Foundry registration should not expose raw Logic Apps callback URLs to the chatbot.

The target strategy is:

```text
MAF agent
  -> approved MCP tool layer
  -> FastAPI / governance checks where needed
  -> Logic Apps Standard workflow endpoints
```

This keeps FastAPI as the enterprise control plane for approval, audit, diagnostics, and secrets.

## Local Preflight

The local preflight module is:

```text
agent/src/foundry/registration_plan.py
```

It verifies:

- `FOUNDRY_PROJECT_ENDPOINT` is configured
- `MODEL_DEPLOYMENT_NAME` is configured
- `FOUNDRY_AGENT_NAME` matches the local agent definition
- the local agent definition declares Microsoft Agent Framework
- the instruction file is present
- approved tool metadata is complete

## Live Registration Result

Step 13 created the first real Foundry agent version.

| Field | Value |
|---|---|
| Agent name | `enterprise-integration-agent` |
| Version | `2` |
| Status | `active` |
| Model deployment | `gpt-4.1-mini` |
| Definition kind | `prompt` |
| Publishing status | not published |

The agent version is now present in the Foundry project, but publishing is still intentionally deferred.

## Invocation Plan

Step 13D adds a Python invocation helper for the active agent version:

```text
agent/src/foundry/live_agent.py
```

The helper invokes `enterprise-integration-agent:1` through the Foundry runtime client. This validates the cloud-side agent response before FastAPI is switched to live Foundry invocation.

Live invocation status:

| Field | Value |
|---|---|
| Test message | `Check order ORD-1001` |
| Result | agent returned parseable JSON planning output |
| Response ID | `resp_0e2b43a3d2fd2b05006a1cb620abdc8194bf405bce04ac66b1` |
| Tool selected by agent response | `getOrderStatus` |
| Parsed entities | `{"order_id": "ORD-1001"}` |
| Execution posture | structured planning only; no Logic Apps execution from Foundry yet |

## FastAPI Runtime Switch

Step 13E adds:

```text
AGENT_RUNTIME_MODE=local
```

Supported modes:

| Mode | Runtime | Backend execution |
|---|---|---|
| `local` | local rule-based adapter | existing MCP and Logic Apps path |
| `foundry` | live Foundry agent invocation | structured planning only |

This lets `/agent/chat` test the live Foundry agent without bypassing FastAPI governance.

## Not Included Yet

- Tool attachment in Foundry
- Agent publishing
- Agent Application RBAC
- Published endpoint invocation

Those belong to later steps.
