# Step 16D - Publish Azure Logic Apps Workflows

## Goal

Publish the local Logic Apps Standard workflow definitions into the Azure Logic App Standard host.

## Azure Host

| Setting | Value |
|---|---|
| Resource group | `rg-sysint-enterprise-integration-eus` |
| Logic App Standard app | `la-sysint-enterprise-integration-eus` |
| Region | Sweden Central |
| Host | `la-sysint-enterprise-integration-eus.azurewebsites.net` |

## Publish Method

The first publish attempt used:

```powershell
func azure functionapp publish la-sysint-enterprise-integration-eus
```

That failed because the local Functions Core Tools compression routine could not load.

The working path is zip deployment:

```powershell
az functionapp deployment source config-zip `
  --resource-group rg-sysint-enterprise-integration-eus `
  --name la-sysint-enterprise-integration-eus `
  --src .azure\logicapp-standard.zip
```

The reusable script is:

```text
infra/scripts/publish-logicapps.ps1
```

## Published Workflows

Azure runtime management shows these workflows as healthy:

| Workflow | State | Trigger |
|---|---|---|
| `checkShipmentStatus` | Healthy | HTTP request |
| `createApprovalRequest` | Healthy | HTTP request |
| `createServiceNowTicket` | Healthy | HTTP request |
| `getOrderStatus` | Healthy | HTTP request |
| `queryIntegrationRunStatus` | Healthy | HTTP request |
| `sendSupplierNotification` | Healthy | HTTP request |
| `validateInvoice` | Healthy | HTTP request |

## Azure Workflow Test

Tested `getOrderStatus` through its Azure callback URL.

The secret callback URL was not printed or committed.

Request payload:

```json
{
  "server_name": "logic-apps-standard-mcp",
  "tool_name": "getOrderStatus",
  "correlation_id": "azure-corr-001",
  "payload": {
    "order_id": "ORD-1001"
  },
  "timeout_seconds": 30
}
```

Response:

```json
{
  "status": "completed",
  "result": {
    "orderNumber": "4500098123",
    "requestedOrderId": "ORD-1001",
    "status": "In Transit",
    "estimatedDeliveryDate": "2026-05-21",
    "delayRisk": "Medium",
    "correlationId": "azure-corr-001"
  },
  "message": "Remote MCP execution completed by local Logic Apps workflow."
}
```

## MCP Server Direction

The next step is to enable the Logic App as an MCP server from Azure so workflows can be exposed as tools.

The intended portal action is:

```text
Create an MCP server
```

After that, the MCP server endpoint and tool metadata should replace individual callback URLs as the preferred enterprise tool exposure path.

## Cost Reminder

The WS1 plan can continue to cost while it exists. Delete the disposable resources when not actively testing.
