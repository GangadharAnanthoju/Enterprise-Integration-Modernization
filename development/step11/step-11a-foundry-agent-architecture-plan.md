# Step 11A - Foundry Agent Architecture Plan

## Goal

Define the Foundry agent architecture before creating a real Foundry-hosted agent.

This step is intentionally documentation-only. It explains what the agent should do, what FastAPI should keep doing, and how the agent connects to MCP and Logic Apps.

## Why Start Here

Foundry tool registration can feel abstract if the agent role is not clear first.

The better learning order is:

```text
1. Define the agent's job
2. Define the agent's instructions
3. Define how tools attach to the agent
4. Register or deploy the agent in Foundry
```

Step 11A covers item 1.

## Current Local Architecture

```text
User
  -> FastAPI /agent/chat
  -> Local rule-based agent adapter
  -> Tool registry
  -> Risk policy
  -> MCP request builder
  -> Remote MCP executor
  -> Local Logic Apps workflow endpoint
```

This works locally, but the "agent brain" is still a transparent Python learning implementation.

## Target Foundry Architecture

```text
User or frontend
  -> FastAPI API boundary
  -> Foundry agent adapter
  -> Foundry-hosted agent runtime
  -> Approved tool selection
  -> MCP execution boundary
  -> Logic Apps workflow endpoint
  -> Enterprise backend system
```

FastAPI stays as the enterprise API boundary. Foundry becomes the agent runtime and governance plane.

## Responsibility Split

| Layer | Responsibility |
|---|---|
| FastAPI | Public API, request validation, response mapping, audit endpoints, operational endpoints |
| Foundry agent | Reason over the user request, ask for missing details, select approved tools, explain decisions |
| Tool registry | Source of truth for approved MCP tools, risk level, required entities, owners, and schema references |
| Risk policy | Decide whether a selected tool can execute directly or requires approval |
| Approval layer | Create, decide, and execute approval-gated actions |
| MCP layer | Build governed envelopes, choose per-tool endpoint, call Logic Apps, normalize responses |
| Logic Apps | Execute enterprise workflows and call backend systems |
| Foundry operations | Evaluations, tracing, monitoring, versioning, and release readiness |

## What The Foundry Agent Should Do

The Foundry agent should:

1. Understand the user's business request.
2. Select only approved tools from the governed catalog.
3. Extract required business entities.
4. Ask a follow-up question when required entities are missing.
5. Respect risk policy.
6. Never execute high-risk tools without approval.
7. Preserve correlation IDs across the workflow.
8. Return structured plans and explanations.

## What The Foundry Agent Should Not Do

The Foundry agent should not:

1. Invent tool names.
2. Call backend systems directly.
3. Bypass the MCP boundary.
4. Bypass approval policy.
5. Hide missing required entities.
6. Put secrets in responses.
7. Decide production deployment or infrastructure changes by itself.

## How This Replaces The Local Agent

Today:

```text
LocalRuleBasedAgentAdapter
  -> handle_chat_message()
```

Later:

```text
FoundryAgentAdapter
  -> Foundry agent runtime
  -> structured plan
  -> same API response shape
```

The FastAPI route should not need to change. It already calls the adapter boundary in `agent/src/foundry/agent_adapter.py`.

## Agent-To-Tool Flow

The future Foundry agent should produce a structured plan similar to:

```json
{
  "tool_name": "getOrderStatus",
  "entities": {
    "order_id": "ORD-1001"
  },
  "reason": "The user asked to check an order status."
}
```

Then the existing backend layers continue:

```text
planned tool
  -> risk policy
  -> missing entity check
  -> approval gate if needed
  -> MCP envelope
  -> Logic Apps endpoint
```

## Foundry First-Class Concerns

When we create the real agent, Foundry should own or support:

| Concern | Foundry role |
|---|---|
| Runtime | Host or orchestrate the agent |
| Instructions | Store/version the agent instructions |
| Tool attachment | Register approved tools or MCP server connection |
| Evaluations | Run safety and regression cases |
| Tracing | Capture plan, tool call, and outcome spans |
| Monitoring | Track failures, approval-required rates, and missing-entity cases |
| Governance | Support release readiness and policy review |

## Next Steps

| Step | Purpose |
|---|---|
| 11B | Write the Foundry agent instruction file |
| 11C | Add a local `foundry/agent.yaml` skeleton |
| 11D | Connect adapter metadata to the agent config |
| 11E | Prepare tool registration mapping after the agent identity is clear |

## Interview Explanation

I did not jump directly into tool registration. First I defined the agent's role in the architecture. The Foundry agent will reason over user requests and select approved tools, but execution remains governed through risk policy, approvals, MCP envelopes, and Logic Apps workflows. This keeps the agent powerful but controlled.
