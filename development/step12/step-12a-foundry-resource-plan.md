# Step 12A - Foundry Resource And Creation Plan

## Goal

Move from local Foundry preparation to a reviewed plan for creating the real Foundry agent.

This step does not create Azure resources. It identifies what must exist before live Foundry agent creation.

## Added File

```text
foundry/governance/foundry-resource-plan.md
```

## What The Plan Covers

- Target runtime shape
- Required Foundry resources
- Project choices to review
- Current local artifacts that support Foundry creation
- Agent creation sequence
- Guardrails
- Open questions

## Why This Step Matters

We already have:

```text
local agent adapter
Foundry instruction file
agent definition skeleton
tool registration metadata
local evaluations
readiness checks
```

Step 12A asks the next practical questions:

- Where will the real Foundry agent live?
- Which model deployment will it use?
- How will tools be attached?
- How do we keep FastAPI as the enterprise control plane?
- What evaluations must pass before demo or release?

## Recommended Direction

Keep this architecture:

```text
Chatbot UI
  -> FastAPI control plane
    -> Foundry Agent
      -> approved MCP tool layer
        -> Logic Apps workflows
```

This keeps the chatbot simple and keeps enterprise enforcement in backend code.

## What We Should Not Do Yet

- Do not create paid Azure resources without review.
- Do not deploy a model before checking capacity and cost.
- Do not expose Logic Apps callback URLs directly to the UI.
- Do not bypass FastAPI approval and audit controls.
- Do not duplicate the approved tool registry manually in Foundry.

## Interview Explanation

After preparing the local Foundry artifacts, I added a resource plan before creating anything in Azure. The plan identifies the Foundry project, model deployment, agent, tool registration, evaluations, and observability pieces needed for a safe live setup. This avoids rushing into cloud resources before cost, region, RBAC, and tool-access design are reviewed.
