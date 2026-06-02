# Step 16E - MCP Tool Description Metadata

## Goal

Prepare the published Logic Apps workflows for MCP server discovery by adding clear tool descriptions and input parameter descriptions.

Microsoft's Logic Apps MCP guidance says the MCP server uses the Request trigger description as the tool description and uses request payload descriptions to help agents pass correct inputs.

Reference:

```text
https://learn.microsoft.com/en-us/azure/logic-apps/create-model-context-protocol-server-standard
```

## What Changed

Updated every workflow in:

```text
logicapps/standard-app
logicapps/workflows
```

Each workflow now has:

- workflow definition description
- Request trigger description
- MCP envelope schema description
- `server_name` description
- `tool_name` description
- `correlation_id` description
- `payload` description
- `timeout_seconds` description
- descriptions for each tool-specific payload field

## Workflows Updated

| Workflow | Discovery Purpose |
|---|---|
| `getOrderStatus` | Read-only order status, estimated delivery, and delay risk lookup |
| `checkShipmentStatus` | Read-only shipment status and delivery progress lookup |
| `validateInvoice` | Invoice readiness and exception validation |
| `queryIntegrationRunStatus` | Integration run troubleshooting by correlation ID |
| `sendSupplierNotification` | Approval-gated supplier notification for a shipment |
| `createServiceNowTicket` | Approval-gated ServiceNow incident creation |
| `createApprovalRequest` | Human approval request creation for governed actions |

## Regression Test

Added a test that fails if any workflow lacks MCP discovery metadata:

```text
agent/tests/test_logicapps_contracts.py
```

Validation:

```text
137 passed
```

## Azure Republish

Republished the workflows after adding descriptions:

```powershell
.\infra\scripts\publish-logicapps.ps1
```

Result:

```text
ZipDeploy succeeded
```

Runtime health check:

```text
checkShipmentStatus        Healthy  False
createApprovalRequest      Healthy  False
createServiceNowTicket     Healthy  False
getOrderStatus             Healthy  False
queryIntegrationRunStatus  Healthy  False
sendSupplierNotification   Healthy  False
validateInvoice            Healthy  False
```

## Next Step

Create or enable the Logic Apps MCP server in Azure:

```text
Logic App -> Agents -> MCP servers -> Create
```

Use existing workflows and select the workflows that should be exposed as tools.
