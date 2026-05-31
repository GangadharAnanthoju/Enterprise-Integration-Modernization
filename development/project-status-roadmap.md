# Enterprise Integration Modernization - Project Status Roadmap

Last updated: 2026-05-31

## Current Position

We have completed through **Step 15**.

The project now has:

- a working FastAPI control plane
- governed tool contracts
- risk policy and approval gates
- MCP request building and execution boundaries
- local Logic Apps Standard workflows acting as MCP tool endpoints
- Microsoft Foundry agent instructions and governance artifacts
- a real Foundry agent version: `enterprise-integration-agent:2`
- live Foundry JSON planning from Python
- a FastAPI runtime switch between local and Foundry modes
- shared governed execution for local and Foundry plans
- a Foundry-ready JSONL evaluation dataset exported from local safety cases

## Current Architecture

```text
User / UI
  -> FastAPI /agent/chat
    -> runtime switch
       -> local rule-based planner
          -> governed MCP execution
          -> local Logic Apps workflows
       -> live Foundry agent
          -> JSON plan
          -> shared governed execution
```

The current safe default is:

```text
AGENT_RUNTIME_MODE=local
```

Foundry mode is available for planning tests:

```text
AGENT_RUNTIME_MODE=foundry
```

In Foundry mode, ready low-risk plans can now execute through the same governed MCP path as local mode when `simulate_when_ready=true`.

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
| Live Foundry agent | Done | Created `enterprise-integration-agent:2` |
| Live Foundry invocation | Done | Invoked active Foundry agent version from Python |
| FastAPI runtime switch | Done | `/agent/chat` can use local or Foundry mode |
| Shared governance execution | Done | Local and Foundry plans use shared backend governance |
| Foundry evaluation foundation | Done | Local safety cases exported into Foundry-ready JSONL |

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
| 14 | Foundry JSON planning and governed execution bridge | Complete |
| 15 | Foundry evaluation dataset strategy and JSONL export | Complete |

## Most Recent Commit

```text
52b94c0 Complete Foundry governed execution step 14
```

This commit was pushed to:

```text
origin/dev
```

## What Is Pending

### Step 15 - Foundry Evaluations

Completed moving local safety cases toward Foundry-ready evaluation assets.

Current asset:

```text
foundry/evaluations/datasets/enterprise-mcp-regression.jsonl
```

Step 15 documentation:

```text
development/step15/step-15a-foundry-evaluation-plan.md
development/step15/step-15b-foundry-evaluation-jsonl-export.md
development/step15/step-15c-step-15-completion.md
```

The dataset is generated from:

```text
agent/src/foundry/evaluation_export.py
```

### Step 16 - Azure Logic Apps Deployment

Move from local Logic Apps to Azure when cost and resource plan are approved.

Pending decisions:

- Logic Apps Standard plan
- storage account
- deployment method
- Key Vault or app settings
- APIM or direct internal endpoint

### Step 17 - Production Hardening

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
Step 16A - Azure Logic Apps Deployment Resource Review
```

First implementation target:

```text
development/step16/step-16a-azure-logic-apps-deployment-plan.md
```

The goal is to decide whether and how to deploy the local Logic Apps Standard project into Azure without creating unnecessary cost.
