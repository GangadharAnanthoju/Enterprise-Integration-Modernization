# Enterprise Integration Modernization - Project Status Roadmap

Last updated: 2026-06-01

## Current Position

We have completed through **Step 15** and started **Step 16**.

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
- confirmed Azure deployment names for a disposable Logic Apps Standard deployment
- deployed disposable Azure Logic Apps Standard infrastructure in Sweden Central
- published all local Logic Apps workflows to the Azure Logic App Standard host
- added MCP discovery descriptions to every workflow Request trigger and payload schema
- enabled the managed Logic Apps MCP server from source-controlled package files
- started connecting the Python agent runtime to the managed Logic Apps MCP endpoint
- verified live FastAPI `/agent/chat` execution through the managed Logic Apps MCP server

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
| Azure Logic Apps infrastructure | Done | WS1 Logic App Standard app, plan, and storage deployed in Sweden Central |
| Azure workflow publishing | Done | Seven Logic Apps workflows published and healthy |
| MCP workflow metadata | Done | Request trigger and input parameter descriptions added for tool discovery |
| Logic App runtime upgrade | Done | `WEBSITE_NODE_DEFAULT_VERSION` updated from `~18` to `~24` |
| Logic Apps MCP server | Done | `enterpriseintegrationmcp` exposes seven workflows as managed MCP tools |
| Agent to managed MCP | Done | Python remote client uses MCP initialize and tools/call |
| Live Azure MCP chat test | Done | `/agent/chat` executed `getOrderStatus` through `enterpriseintegrationmcp` |

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
| 16 | Azure Logic Apps Standard deployment, workflow publishing, MCP metadata, and MCP server enablement | Complete |
| 17 | Agent integration with managed Logic Apps MCP server | Complete |

## Most Recent Commit

```text
5e9ad38 Complete Foundry evaluation step 15
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

Move from local Logic Apps to Azure using a disposable, low-cost learning deployment.

Confirmed values:

| Setting | Value |
|---|---|
| Resource group | `rg-sysint-enterprise-integration-eus` |
| Logic App Standard app | `la-sysint-enterprise-integration-eus` |
| Region | `swedencentral` |
| Plan | `asp-sysint-enterprise-integration-eus` |
| SKU | `WS1` |
| Storage | `stsysintintegeus001` |

Current deployment files:

```text
infra/main.bicep
infra/modules/storage.bicep
infra/modules/logicapp.bicep
infra/parameters.dev.json
infra/scripts/deploy-dev.ps1
infra/scripts/destroy-dev.ps1
```

Step 16 documentation:

```text
development/step16/step-16a-azure-logic-apps-deployment-plan.md
development/step16/step-16b-azure-bicep-validation.md
development/step16/step-16c-azure-logic-apps-infra-deployment.md
development/step16/step-16d-publish-azure-workflows.md
development/step16/step-16e-mcp-tool-description-metadata.md
development/step16/step-16f-node-runtime-upgrade.md
development/step16/step-16g-enable-logic-apps-mcp-server.md
```

Validation result:

```text
Local bicep build: passed
Azure deployment validation in East US: blocked by quota
Azure deployment validation in Sweden Central: passed
Azure infrastructure deployment in Sweden Central: succeeded
Azure workflow zip deployment: succeeded
Azure getOrderStatus callback test: succeeded
MCP discovery metadata test: passed
Node.js app setting: WEBSITE_NODE_DEFAULT_VERSION=~24
Workflow health after Node upgrade: healthy
Logic Apps MCP server listing: succeeded
```

Deployed resources:

```text
la-sysint-enterprise-integration-eus.azurewebsites.net
asp-sysint-enterprise-integration-eus
stsysintintegeus001
```

Still pending:

- update MCP endpoint environment values
- connect the agent to the managed Logic Apps MCP server endpoint
- delete resources when finished testing

### Step 17 - Agent To Managed Logic Apps MCP

Current target:

```text
Connect FastAPI /agent/chat to enterpriseintegrationmcp
```

Step 17 documentation:

```text
development/step17/step-17a-agent-to-managed-logic-apps-mcp.md
development/step17/step-17b-live-fastapi-managed-mcp-test.md
```

Current verification:

```text
MCP transport focused tests: 25 passed
VS Code MCP discovery: 7 tools discovered
Live FastAPI remote MCP chat test: passed
```

Still pending:

- test high-risk approval flow against managed MCP after approval
- decide when to delete the disposable Azure resources

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
Step 18A - Production Hardening Plan
```

First implementation target:

```text
Plan persistent audit, approvals, Key Vault, managed identity, and observability
```

The goal is to move from a working learning deployment to enterprise-grade operations.
