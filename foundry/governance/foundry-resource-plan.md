# Foundry Resource Plan

This plan describes the Azure AI Foundry resources needed before creating the real enterprise integration agent.

It is intentionally a review document. Do not create Azure resources from this file until the project, region, model, cost, and RBAC choices are approved.

## Target Runtime Shape

```text
Chatbot UI
  -> FastAPI control plane
    -> Microsoft Agent Framework agent in Foundry
      -> approved MCP tool layer
        -> Logic Apps Standard workflows
```

FastAPI remains the enterprise control plane for API contracts, approval enforcement, audit events, readiness checks, diagnostics, and secret isolation.

## Required Foundry Resources

| Resource | Purpose | Status |
|---|---|---|
| Azure AI Foundry project | Hosts the agent, evaluations, traces, and project-scoped configuration | Not created by this step |
| Azure AI Services / Foundry account | Parent AI resource for model access and Foundry project operations | To be confirmed |
| Model deployment | Reasoning model used by the Foundry agent | To be selected |
| MAF-backed Foundry agent | Agent using Microsoft Agent Framework, project instructions, and tool metadata | Future step |
| Tool registration | Connects the agent to approved MCP tools or an MCP gateway/facade | Future step |
| Evaluation dataset | Regression cases for tool selection, missing entities, and approval gating | Future step |

## Project Choices To Review

| Choice | Recommended Starting Point | Notes |
|---|---|---|
| Resource group | Existing enterprise integration resource group, if suitable | Keep cost and ownership clear |
| Region | Same region as current integration resources, if capacity exists | Confirm model availability before deploying |
| Model | Small capable model first | Keep cost low for learning/demo |
| Agent framework | Microsoft Agent Framework | Keep MAF as the implementation path |
| Tool access | MCP tool layer behind FastAPI or API gateway | Avoid exposing Logic Apps callback URLs directly to the agent/UI |
| Authentication | Managed identity/RBAC where possible | Avoid local secrets in production |
| Observability | Foundry traces plus App Insights projection | Correlation ID should connect every step |

## Current Local Artifacts

| Artifact | Purpose |
|---|---|
| `agent/src/prompts/foundry_agent_instructions.md` | Future Foundry agent behavior instructions |
| `foundry/agent-definitions/enterprise-integration-agent.yaml` | Local agent definition skeleton |
| `agent/src/foundry/tool_registration.py` | Foundry-facing tool metadata projected from the approved registry |
| `agent/src/foundry/evaluations.py` | Local evaluation cases that can become Foundry eval dataset rows |
| `agent/src/foundry/governance.py` | Readiness checks for local Foundry preparation |

## Agent Creation Sequence

1. Confirm Foundry project or create one.
2. Confirm model deployment name and capacity.
3. Register or create the MAF-backed Foundry agent using the instruction file.
4. Attach approved tools through an MCP-compatible layer.
5. Run evaluation cases before demo or release.
6. Connect traces and monitoring.
7. Keep FastAPI as the enterprise control plane.

## Guardrails

- Do not let the agent invent tools.
- Do not expose Logic Apps callback signatures to the chatbot.
- Do not let high-risk actions bypass approval.
- Do not duplicate the tool catalog manually in Foundry.
- Do not treat prompt instructions as the only safety layer.
- Keep MCP as the backend execution path.

## Open Questions

- Which Foundry project should host the agent?
- Which model deployment should the agent use?
- Should the first live Foundry agent be prompt-based or hosted?
- Should tool access go through FastAPI, APIM, a dedicated MCP facade, or direct Foundry tool registration?
- Which evaluations are required before a public demo?
