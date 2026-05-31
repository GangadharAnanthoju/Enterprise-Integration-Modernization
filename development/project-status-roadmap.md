# Enterprise Integration Modernization - Project Status Roadmap

Last updated: 2026-05-30

## Current Position

We have completed through **Step 13** and started **Step 14**.

The project now has:

- a working FastAPI control plane
- governed tool contracts
- risk policy and approval gates
- MCP request building and execution boundaries
- local Logic Apps Standard workflows acting as MCP tool endpoints
- Microsoft Foundry agent instructions and governance artifacts
- a real Foundry agent version: `enterprise-integration-agent:1`
- live Foundry invocation from Python
- a FastAPI runtime switch between local and Foundry planning modes

## Current Architecture

```text
User / UI
  -> FastAPI /agent/chat
    -> runtime switch
       -> local rule-based planner
          -> governed MCP execution
          -> local Logic Apps workflows
       -> live Foundry agent
          -> planning-only response
```

The current safe default is:

```text
AGENT_RUNTIME_MODE=local
```

Foundry mode is available for planning tests:

```text
AGENT_RUNTIME_MODE=foundry
```

In Foundry mode, backend execution is intentionally disabled for now.

## Completed Milestones

| Area | Status | What We Built |
|---|---|---|
| Tool catalog | Done | Approved enterprise MCP tool registry |
| Risk policy | Done | Low/medium tools can run, high-risk tools require approval |
| Agent shell | Done | Local planning, entity extraction, missing entity checks |
| Approval flow | Done | Create, decide, and execute approved high-risk requests |
| Audit and traces | Done | Audit events, Foundry-style traces, App Insights-style envelopes |
| Evaluations | Done | Local Foundry-style safety evaluation suite |
| MCP boundary | Done | Mock and remote executor boundary |
| Remote MCP HTTP | Done | HTTP client, auth headers, response normalization, errors |
| Environment validation | Done | MCP, Foundry, Azure, and observability checks |
| Logic Apps local workflows | Done | Local workflows for order, shipment, invoice, run status, and high-risk actions |
| Foundry preparation | Done | Agent definition, instructions, tool metadata, readiness checks |
| MAF preparation | Done | Local Microsoft Agent Framework-shaped skeleton |
| Live Foundry agent | Done | Created `enterprise-integration-agent:1` |
| Live Foundry invocation | Done | Invoked active Foundry agent version from Python |
| FastAPI runtime switch | Done | `/agent/chat` can use local mode or Foundry planning mode |

## Step Summary

| Step | Theme | Status |
|---|---|---|
| 2 | Tool catalog, risk policy, mock simulation, first chat shell | Complete |
| 3 | Intent detection, entity extraction, planned action, approval flow | Complete |
| 4 | Audit, observability, local evaluations, readiness checks | Complete |
| 5 | Tool contracts, MCP request payloads, Foundry adapter boundary | Complete |
| 6 | MCP executor boundary and diagnostics | Complete |
| 7 | Remote MCP HTTP contract and client | Complete |
| 8 | Environment setup and validation | Complete |
| 9 | Logic Apps Standard local project and workflow design | Complete |
| 10 | Local Logic Apps as remote MCP endpoints | Complete |
| 11 | Foundry agent architecture, instructions, and tool metadata | Complete |
| 12 | Real Foundry resource plan and MAF skeleton | Complete |
| 13 | Live Foundry agent creation, invocation, and FastAPI switch | Complete |

## Most Recent Commit

```text
9c0e713 Complete Foundry live invocation step 13
```

This commit was pushed to:

```text
origin/dev
```

## What Is Pending

### Step 14 - Foundry Tool Execution Strategy

Decide how the live Foundry agent should connect to governed tools.

Recommended direction:

```text
Foundry Agent
  -> produces structured plan
  -> FastAPI validates and enforces governance
  -> MCP executor calls Logic Apps
```

Why:

- Foundry stays first-class for reasoning.
- FastAPI remains the enterprise control plane.
- MCP remains the backend execution boundary.
- Logic Apps callback URLs and secrets stay out of the agent/UI.
- Risk policy and approvals remain enforceable in backend code.

Step 14A is documented in:

```text
development/step14/step-14a-foundry-tool-execution-strategy.md
```

Step 14B adds the first structured plan contract in:

```text
agent/src/foundry/planning.py
development/step14/step-14b-structured-foundry-plan-contract.md
```

Step 14C updates the Foundry instructions to request JSON planning output:

```text
agent/src/prompts/foundry_agent_instructions.md
development/step14/step-14c-foundry-json-planning-instructions.md
```

Step 14D created and verified the live JSON-planning Foundry version:

```text
enterprise-integration-agent:2
development/step14/step-14d-live-foundry-json-plan-verification.md
```

Live verification result:

```text
selected_tool=getOrderStatus
entities={"order_id": "ORD-1001"}
ready_for_governance=true
```

Step 14E connects the Foundry adapter to the parser:

```text
AGENT_RUNTIME_MODE=foundry
  -> live Foundry response
  -> parse_foundry_action_plan
  -> PlannedAction response
  -> no backend execution yet
```

Step 14F documents the governed execution bridge:

```text
Foundry PlannedAction
  -> shared FastAPI governance
  -> MCP executor
  -> Logic Apps workflow
```

Implementation is still pending. The next code step should extract the local governance execution flow into a shared function so local and Foundry modes use the same enforcement logic.

Step 14G extracts that shared function:

```text
agent/src/agent_contracts.py
agent/src/agent_execution.py
```

Local mode now routes selected tools through `execute_planned_action`. Foundry mode still stops at structured planning until the next step connects it to the same function.

Step 14H connects Foundry mode to the same function:

```text
Foundry JSON plan
  -> execute_planned_action
  -> missing entity, approval, or MCP execution
```

Live Step 14H verification:

```text
AGENT_RUNTIME_MODE=foundry
FOUNDRY_AGENT_VERSION=2
message="Check order ORD-1001"
status=completed
tool_called=true
selected_tool=getOrderStatus
mcp_mode=mock
```

### Step 15 - Complete Step 14 And Commit

Step 14 now has a substantial set of code, docs, live Foundry changes, and tests.

Before moving to Azure deployment or evaluations, commit and push the Step 14 milestone.

### Step 16 - Azure Logic Apps Deployment

Move from local Logic Apps to Azure when cost and resource plan are approved.

Pending decisions:

- Logic Apps Standard plan
- storage account
- deployment method
- Key Vault or app settings
- APIM or direct internal endpoint

### Step 17 - Foundry Evaluations

Move local evaluation cases into Foundry evaluation assets.

Focus areas:

- tool selection accuracy
- missing entity behavior
- high-risk approval gating
- unsupported request handling
- response consistency

### Step 18 - Production Hardening

Future enterprise hardening:

- persistent audit storage
- persistent approval storage
- managed identity
- Key Vault
- App Insights / Log Analytics
- APIM policies
- RBAC
- deployment pipeline

## Recommended Next Step

Start:

```text
Step 14H - Foundry Plan Uses Shared Governance Execution
```

First implementation target:

```text
agent/src/foundry/agent_adapter.py
```

The goal is to let Foundry mode call `execute_planned_action` after successful JSON plan parsing.
