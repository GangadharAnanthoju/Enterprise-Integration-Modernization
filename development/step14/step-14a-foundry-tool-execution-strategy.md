# Step 14A - Foundry Tool Execution Strategy

## Goal

Decide how the live Microsoft Foundry agent should participate in tool execution without bypassing enterprise governance.

Step 13 proved that the Foundry agent can be created, invoked, and reached through FastAPI. Step 14 decides how that agent should move from planning into governed backend action.

## Decision

Use this strategy:

```text
Foundry Agent
  -> produces a structured action plan
  -> FastAPI validates and enforces governance
  -> MCP executor builds the request envelope
  -> Logic Apps workflow executes the backend action
```

In short:

```text
Foundry reasons.
FastAPI governs.
MCP executes.
Logic Apps integrates.
```

## Why This Is The Best Fit For This Project

The project is an enterprise integration modernization initiative, not only a chatbot demo.

That means backend execution must remain controlled by deterministic services and policies:

- approved tool registry
- required entity validation
- risk policy
- approval gates
- audit events
- correlation IDs
- MCP envelope construction
- endpoint and secret isolation

The Foundry agent should not directly call Logic Apps callback URLs yet. Those URLs are operational endpoints and may include secrets. They should stay behind the backend control plane.

## Recommended Architecture

```text
User / Chat UI
  -> FastAPI /agent/chat
    -> Foundry Agent
      -> structured plan only
    -> FastAPI plan validator
      -> approved tool registry
      -> required entity checks
      -> risk policy
      -> approval workflow if needed
    -> MCP executor
      -> Logic Apps workflow endpoint
    -> normalized response
```

## What Foundry Should Return Next

Foundry should return a structured planning object, not free-form execution text.

Target shape:

```json
{
  "selected_tool": "getOrderStatus",
  "entities": {
    "order_id": "ORD-1001"
  },
  "requires_clarification": false,
  "clarification_question": null,
  "confidence": "high",
  "reason": "The user asked to check the status of order ORD-1001."
}
```

For missing data:

```json
{
  "selected_tool": "getOrderStatus",
  "entities": {},
  "requires_clarification": true,
  "clarification_question": "Please provide the order ID.",
  "confidence": "medium",
  "reason": "The user asked for order status but did not provide an order ID."
}
```

For unsupported requests:

```json
{
  "selected_tool": null,
  "entities": {},
  "requires_clarification": true,
  "clarification_question": "I can help with approved order, shipment, invoice, supplier, ticket, approval, or integration run-status workflows.",
  "confidence": "low",
  "reason": "No approved enterprise integration tool matches the request."
}
```

## What FastAPI Must Still Enforce

FastAPI must treat the Foundry plan as untrusted input.

Even if the Foundry agent selects a tool, FastAPI must independently check:

- tool exists in `agent/src/tools/registry.py`
- selected tool is approved
- required entities are present
- no unexpected tool name was invented
- risk policy allows direct execution
- high-risk tools have approval before execution
- MCP request payload is built from the contract, not raw model text

## Execution Rules

| Scenario | Foundry role | FastAPI role | MCP / Logic Apps role |
|---|---|---|---|
| Low-risk ready request | Select tool and entities | Validate and execute | Run workflow |
| Missing required entity | Ask for missing data | Return clarification | No call |
| High-risk ready request | Select tool and entities | Create approval request | No call until approved |
| Approved high-risk request | Not required | Validate approval and execute | Run workflow |
| Unsupported request | Return no selected tool | Return clarification | No call |
| Invented tool | Might be returned by mistake | Reject it | No call |

## Why Not Attach Logic Apps Directly To Foundry Now?

Direct attachment is possible later, but it is not the safest next step for this learning project.

Risks of direct attachment too early:

- model could request a tool before backend approval checks
- Logic Apps callback URLs or auth details could become too close to the agent layer
- high-risk approvals may be harder to enforce consistently
- audit and correlation logic could split across multiple places
- tests would become more integration-heavy before the contract is stable

Direct tool attachment can be revisited after structured planning, evaluations, and backend enforcement are stable.

## Future Options

### Option A - Current Recommendation

```text
Foundry plan -> FastAPI governance -> MCP executor -> Logic Apps
```

Best for this project now.

### Option B - Dedicated MCP Facade

```text
Foundry agent -> enterprise MCP facade -> Logic Apps
```

Good future production option if the MCP facade itself enforces registry, auth, policy, approval, and audit.

### Option C - Direct Foundry Tool Attachment

```text
Foundry agent -> tool endpoint -> Logic Apps
```

Useful for simple or low-risk demos, but weaker for this enterprise governance narrative unless the endpoint is heavily protected.

## Step 14B Preview

Next, define the structured Foundry plan contract in code.

Likely files:

```text
agent/src/foundry/planning.py
agent/tests/test_foundry_planning.py
agent/src/prompts/foundry_agent_instructions.md
```

The goal of Step 14B should be:

```text
Convert Foundry's response into a validated structured plan object.
```

No MCP execution should be added until the plan contract is stable.

## Interview Explanation

I intentionally kept Foundry as the reasoning layer and FastAPI as the enforcement layer. In enterprise integration, the model should not be the final authority for tool execution. The model can propose a tool and extract entities, but backend code must validate the tool against the registry, enforce required entities, apply risk policy, create approvals, record audit events, and only then call MCP and Logic Apps.
