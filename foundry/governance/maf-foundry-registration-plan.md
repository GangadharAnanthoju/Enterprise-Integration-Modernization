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

## Not Included Yet

- Live Foundry agent creation
- Tool attachment in Foundry
- Agent publishing
- Agent Application RBAC
- Published endpoint invocation

Those belong to later steps.
