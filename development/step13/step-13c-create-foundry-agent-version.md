# Step 13C - Create Foundry Agent Version

## Goal

Use the live Foundry client to create the first real Foundry agent version for this project.

## Agent Created

| Field | Value |
|---|---|
| Agent name | `enterprise-integration-agent` |
| Version | `1` |
| Status | `active` |
| Model deployment | `gpt-4.1-mini` |
| Project endpoint | `https://ms-foundry-sysint-02.services.ai.azure.com/api/projects/proj-sysint-01` |
| Definition kind | `prompt` |
| Temperature | `0.2` |

## What Was Sent To Foundry

The created version uses:

- instructions from `agent/src/prompts/foundry_agent_instructions.md`
- model deployment from `MODEL_DEPLOYMENT_NAME`
- agent name from `FOUNDRY_AGENT_NAME`
- metadata showing this is a Microsoft Agent Framework and MCP-governed project

## What This Means

The project now has a real Foundry agent version in the configured Foundry project.

This is still not the final production runtime. It is the first cloud-side agent version we can test, evaluate, and later connect to tools.

## What Is Not Done Yet

- live agent invocation from code
- MCP tool attachment inside Foundry
- Foundry agent publishing
- chatbot UI connection to the Foundry-hosted agent
- production RBAC and endpoint hardening

## Learning Point

Creating an agent version is different from publishing an agent application.

```text
Create version
  -> agent exists inside Foundry project for testing and iteration

Publish
  -> promote a tested version to a stable application endpoint
```

For this project, we created the version first and kept publishing for a later step.
