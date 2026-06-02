# Step 16G - Enable Logic Apps MCP Server

## Goal

Expose the Azure Logic Apps Standard workflows through the managed Logic Apps MCP server endpoint.

## Problem Observed

The MCP server appeared in the Azure portal briefly, then disappeared.

Activity log showed:

```text
Operation: ListMcpServers
Error code: McpServerNotEnabled
Message: The logic app isn't set up as an MCP server.
```

## Root Cause

This Logic App is deployed by zip package. Portal-only MCP server changes are not reliable for this setup because the deployed package is the source of truth.

## Fix

Keep MCP enablement in source-controlled Logic Apps files:

```text
logicapps/standard-app/host.json
logicapps/standard-app/mcpservers.json
```

The package publish script now includes:

```text
logicapps/standard-app/mcpservers.json
```

## MCP Server

Name:

```text
enterpriseintegrationmcp
```

Tools:

```text
getOrderStatus
checkShipmentStatus
validateInvoice
queryIntegrationRunStatus
createApprovalRequest
sendSupplierNotification
createServiceNowTicket
```

## Verification

After republishing and restarting the Logic App, this management call returned the MCP server and all seven tools:

```powershell
az rest `
  --method post `
  --url "https://management.azure.com/subscriptions/<subscription-id>/resourceGroups/rg-sysint-enterprise-integration-eus/providers/Microsoft.Web/sites/la-sysint-enterprise-integration-eus/hostruntime/runtime/webhooks/workflow/api/management/listMcpServers?api-version=2018-11-01" `
  --body "{}" `
  --output json
```

Workflow health remained healthy for all seven workflows.

## Learning Note

For interview explanation:

```text
We treated the Logic App package as the deployment source of truth. Instead of relying on Portal-only MCP changes, we versioned the MCP server definition and host enablement alongside the workflows, then validated the managed MCP server through Azure management APIs.
```
