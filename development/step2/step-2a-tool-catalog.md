# Step 2A: Tool Catalog in Code

## What We Built

We created the first real governance building block: a static catalog of approved MCP tools.

This is not the AI agent yet. It is the list of enterprise workflows the agent is allowed to know about.

## Why This Matters

For an Azure Integration specialist, think of this as the tool version of an API catalog:

- Each Logic Apps workflow has a tool name.
- Each tool has an owner, business domain, backend system, version, and schema references.
- Each tool has a risk level.
- High-risk tools require approval before they can cause side effects.

## Tools Added

| Tool | Domain | Risk | Approval |
|---|---|---:|---|
| `getOrderStatus` | Order Management | Low | No |
| `validateInvoice` | Finance | Medium | No |
| `checkShipmentStatus` | Logistics | Low | No |
| `sendSupplierNotification` | Supplier Management | High | Yes |
| `createApprovalRequest` | Governance | Medium | No |
| `createServiceNowTicket` | IT Service Management | High | Yes |
| `queryIntegrationRunStatus` | Operations | Low | No |

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/tools/contracts.py` | Defines `RiskLevel` and `ToolContract`. |
| `agent/src/tools/registry.py` | Stores the approved MCP tool catalog. |
| `agent/tests/test_tool_registry.py` | Proves the catalog contains expected tools and approval rules. |

## Key Learning

The agent should not decide freely what enterprise actions exist. We first give it an approved catalog. Later, the agent will select from this catalog, and MCP will execute the matching Logic Apps workflow.

## Next Step

Step 2B will add the risk policy:

- Low risk: allow execution.
- Medium risk: allow execution with audit.
- High risk: require approval.
