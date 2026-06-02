# Logic Apps Azure Deployment Guide

This guide documents exactly how we deployed the Logic Apps Standard workflows for the Enterprise Integration Modernization project.

## Current Deployment

| Item | Value |
|---|---|
| Resource group | `rg-sysint-enterprise-integration-eus` |
| Logic App Standard app | `la-sysint-enterprise-integration-eus` |
| Workflow Standard plan | `asp-sysint-enterprise-integration-eus` |
| Storage account | `stsysintintegeus001` |
| Azure region | `swedencentral` |
| Plan SKU | `WS1` |
| Logic App host | `la-sysint-enterprise-integration-eus.azurewebsites.net` |

The resource names still use the `eus` suffix, but the actual deployment region is Sweden Central because East US WS1 validation was blocked by quota.

## Why Sweden Central

East US validation failed with:

```text
SubscriptionIsOverQuotaForSku
Current Limit (Total VMs): 0
Amount required: 1
```

Sweden Central validation passed, so we deployed there.

## Step 1 - Validate Bicep Locally

From the repo root:

```powershell
bicep build infra\main.bicep
```

Result:

```text
Passed
```

The generated `infra/main.json` is build output and is ignored by git.

## Step 2 - Validate Against Azure Without Creating Resources

East US validation:

```powershell
az deployment group validate `
  --resource-group rg-sysint-enterprise-integration-eus `
  --template-file infra\main.bicep `
  --parameters @infra\parameters.dev.json `
  --parameters location=eastus
```

Result:

```text
Blocked by quota
```

Sweden Central validation:

```powershell
az deployment group validate `
  --resource-group rg-sysint-enterprise-integration-eus `
  --template-file infra\main.bicep `
  --parameters @infra\parameters.dev.json `
  --parameters location=swedencentral
```

Result:

```text
Succeeded
```

## Step 3 - Deploy Minimum Azure Infrastructure

Command used:

```powershell
az deployment group create `
  --resource-group rg-sysint-enterprise-integration-eus `
  --template-file infra\main.bicep `
  --parameters @infra\parameters.dev.json `
  --parameters location=swedencentral
```

Result:

```text
Succeeded
```

Created:

- Logic App Standard app
- WS1 Workflow Standard plan
- Standard_LRS storage account

## Step 4 - Confirm Created Resources

Logic App:

```powershell
az resource show `
  --resource-group rg-sysint-enterprise-integration-eus `
  --resource-type Microsoft.Web/sites `
  --name la-sysint-enterprise-integration-eus `
  --query "{name:name, location:location, state:properties.state, defaultHostName:properties.defaultHostName}" `
  --output json
```

Plan:

```powershell
az resource show `
  --resource-group rg-sysint-enterprise-integration-eus `
  --resource-type Microsoft.Web/serverfarms `
  --name asp-sysint-enterprise-integration-eus `
  --query "{name:name, location:location, sku:sku.name, tier:sku.tier}" `
  --output json
```

Storage:

```powershell
az resource show `
  --resource-group rg-sysint-enterprise-integration-eus `
  --resource-type Microsoft.Storage/storageAccounts `
  --name stsysintintegeus001 `
  --query "{name:name, location:location, sku:sku.name, kind:kind}" `
  --output json
```

## Step 4A - Upgrade Node.js Runtime Setting

Azure Portal warned that Node.js 18 LTS reached end of life on 2025-04-30.

Azure Functions runtime 4.x currently supports Node.js 22 and Node.js 24, so the Logic App app setting was updated from:

```text
WEBSITE_NODE_DEFAULT_VERSION=~18
```

to:

```text
WEBSITE_NODE_DEFAULT_VERSION=~24
```

Command:

```powershell
az functionapp config appsettings set `
  --resource-group rg-sysint-enterprise-integration-eus `
  --name la-sysint-enterprise-integration-eus `
  --settings WEBSITE_NODE_DEFAULT_VERSION=~24
```

Restart:

```powershell
az functionapp restart `
  --resource-group rg-sysint-enterprise-integration-eus `
  --name la-sysint-enterprise-integration-eus
```

Verify:

```powershell
az functionapp config appsettings list `
  --resource-group rg-sysint-enterprise-integration-eus `
  --name la-sysint-enterprise-integration-eus `
  --query "[?name=='WEBSITE_NODE_DEFAULT_VERSION'].{name:name,value:value}" `
  --output json
```

Expected:

```json
[
  {
    "name": "WEBSITE_NODE_DEFAULT_VERSION",
    "value": "~24"
  }
]
```

## Step 5 - Publish Workflows

The first attempt used Functions Core Tools:

```powershell
func azure functionapp publish la-sysint-enterprise-integration-eus
```

That failed locally because the underlying compression routine could not load.

So we used zip deployment instead.

Reusable script:

```powershell
.\infra\scripts\publish-logicapps.ps1
```

Manual package command used:

```powershell
$packageRoot = Join-Path (Get-Location) ".azure"
if (-not (Test-Path $packageRoot)) {
  New-Item -ItemType Directory -Path $packageRoot | Out-Null
}

$staging = Join-Path $packageRoot "logicapp-package"
if (Test-Path $staging) {
  Remove-Item -LiteralPath $staging -Recurse -Force
}

New-Item -ItemType Directory -Path $staging | Out-Null

Copy-Item -Path `
  logicapps\standard-app\host.json, `
  logicapps\standard-app\connections.json, `
  logicapps\standard-app\parameters.json, `
  logicapps\standard-app\mcpservers.json `
  -Destination $staging

$workflowNames = @(
  "checkShipmentStatus",
  "createApprovalRequest",
  "createServiceNowTicket",
  "getOrderStatus",
  "queryIntegrationRunStatus",
  "sendSupplierNotification",
  "validateInvoice"
)

foreach ($name in $workflowNames) {
  $target = Join-Path $staging $name
  New-Item -ItemType Directory -Path $target | Out-Null
  Copy-Item -Path (Join-Path (Join-Path "logicapps\standard-app" $name) "workflow.json") `
    -Destination $target
}

$zipPath = Join-Path $packageRoot "logicapp-standard.zip"
if (Test-Path $zipPath) {
  Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $zipPath
```

Manual zip deploy command used by the script:

```powershell
az functionapp deployment source config-zip `
  --resource-group rg-sysint-enterprise-integration-eus `
  --name la-sysint-enterprise-integration-eus `
  --src .azure\logicapp-standard.zip
```

Result:

```text
Succeeded
```

## Step 6 - Confirm Published Workflows

Command:

```powershell
az rest `
  --method get `
  --url "https://management.azure.com/subscriptions/<subscription-id>/resourceGroups/rg-sysint-enterprise-integration-eus/providers/Microsoft.Web/sites/la-sysint-enterprise-integration-eus/hostruntime/runtime/webhooks/workflow/api/management/workflows?api-version=2018-11-01" `
  --query "[].{name:name,state:health.state,disabled:isDisabled}" `
  --output table
```

Published workflows:

```text
checkShipmentStatus        Healthy  False
createApprovalRequest      Healthy  False
createServiceNowTicket     Healthy  False
getOrderStatus             Healthy  False
queryIntegrationRunStatus  Healthy  False
sendSupplierNotification   Healthy  False
validateInvoice            Healthy  False
```

## Step 7 - Test One Workflow

Get the callback URL without printing it:

```powershell
$callback = az rest `
  --method post `
  --url "https://management.azure.com/subscriptions/<subscription-id>/resourceGroups/rg-sysint-enterprise-integration-eus/providers/Microsoft.Web/sites/la-sysint-enterprise-integration-eus/hostruntime/runtime/webhooks/workflow/api/management/workflows/getOrderStatus/triggers/When_an_HTTP_request_is_received/listCallbackUrl?api-version=2018-11-01" `
  --body "{}" `
  --query value `
  --output tsv
```

Invoke the workflow:

```powershell
$body = @{
  server_name = "logic-apps-standard-mcp"
  tool_name = "getOrderStatus"
  correlation_id = "azure-corr-001"
  payload = @{
    order_id = "ORD-1001"
  }
  timeout_seconds = 30
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Method Post `
  -Uri $callback `
  -ContentType "application/json" `
  -Body $body
```

Result:

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

## Step 8 - Enable Logic Apps MCP Server Metadata

Before creating the MCP server, make sure every workflow has MCP-friendly metadata.

Microsoft's Logic Apps MCP guidance says:

- the Request trigger description becomes the tool description for MCP clients
- request payload property descriptions help agents pass correct inputs

Reference:

```text
https://learn.microsoft.com/en-us/azure/logic-apps/create-model-context-protocol-server-standard
```

In this project, each workflow now includes:

- Request trigger description
- MCP envelope schema description
- `server_name`, `tool_name`, `correlation_id`, `payload`, and `timeout_seconds` descriptions
- descriptions for tool-specific payload fields such as `order_id`, `shipment_id`, `invoice_id`, and `correlation_id`

The metadata was validated with:

```powershell
cd agent
.\.venv\Scripts\python.exe -m pytest tests\test_logicapps_contracts.py
```

## Step 9 - Source-Control The MCP Server

Because this Logic App is deployed by zip package, Portal-only MCP server changes can disappear on the next package load or deployment. Keep MCP server enablement in the deployed package.

Host configuration:

```json
{
  "extensions": {
    "workflow": {
      "McpServerEndpoints": {
        "enable": true,
        "authentication": {
          "type": "ApiKey"
        }
      }
    }
  }
}
```

MCP server definition:

```text
logicapps/standard-app/mcpservers.json
```

The publish script must include this file in the zip package:

```powershell
Copy-Item -Path `
  logicapps\standard-app\host.json, `
  logicapps\standard-app\connections.json, `
  logicapps\standard-app\parameters.json, `
  logicapps\standard-app\mcpservers.json `
  -Destination $staging
```

Then republish:

```powershell
.\infra\scripts\publish-logicapps.ps1
```

Restart:

```powershell
az functionapp restart `
  --resource-group rg-sysint-enterprise-integration-eus `
  --name la-sysint-enterprise-integration-eus
```

Verify MCP server listing:

```powershell
az rest `
  --method post `
  --url "https://management.azure.com/subscriptions/<subscription-id>/resourceGroups/rg-sysint-enterprise-integration-eus/providers/Microsoft.Web/sites/la-sysint-enterprise-integration-eus/hostruntime/runtime/webhooks/workflow/api/management/listMcpServers?api-version=2018-11-01" `
  --body "{}" `
  --output json
```

Expected MCP server:

```text
enterpriseintegrationmcp
```

Exposed tools:

```text
getOrderStatus
checkShipmentStatus
validateInvoice
queryIntegrationRunStatus
createApprovalRequest
sendSupplierNotification
createServiceNowTicket
```

## Step 10 - Manual Portal Step: Authentication And API Key

The previous step proves that Azure recognizes the MCP server. The next step is intentionally manual because the MCP API key is sensitive and Azure shows the generated key only once.

In Azure Portal:

1. Open the Logic App Standard resource:

```text
la-sysint-enterprise-integration-eus
```

2. In the left menu, go to:

```text
Agents -> MCP servers
```

3. Confirm this server exists:

```text
enterpriseintegrationmcp
```

4. Under Authentication, choose:

```text
Key-based
```

5. Select:

```text
Generate key
```

6. Choose:

```text
Primary key
```

7. Copy the generated key immediately and store it only in your local secret file, not in git.

Suggested local agent setting:

```text
agent/.env
```

Example values:

```text
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_SERVER_NAME=logic-apps-standard-mcp
MCP_SERVER_URL=https://la-sysint-enterprise-integration-eus.azurewebsites.net/api/mcpservers/enterpriseintegrationmcp/mcp
MCP_API_KEY=<paste-generated-key-here>
```

Do not paste the key into:

```text
.env.example
docs/
development/
git commits
chat messages
```

## Step 11 - Manual Client Test In VS Code

After the key is generated, test the MCP server from VS Code.

Recommended workspace config:

```text
.vscode/mcp.json
```

Use this shape so VS Code prompts for the key without saving it in plain text:

```json
{
  "servers": {
    "enterpriseintegrationmcp": {
      "type": "http",
      "url": "https://la-sysint-enterprise-integration-eus.azurewebsites.net/api/mcpservers/enterpriseintegrationmcp/mcp",
      "headers": {
        "X-API-Key": "${input:logicAppsMcpApiKey}"
      }
    }
  },
  "inputs": [
    {
      "id": "logicAppsMcpApiKey",
      "type": "promptString",
      "description": "Logic Apps MCP API key",
      "password": true
    }
  ]
}
```

In VS Code:

1. Open Command Palette.
2. Run:

```text
MCP: Add Server
```

3. Choose:

```text
HTTP
```

4. Enter the server URL:

```text
https://la-sysint-enterprise-integration-eus.azurewebsites.net/api/mcpservers/enterpriseintegrationmcp/mcp
```

5. Enter a server ID:

```text
enterpriseintegrationmcp
```

6. When prompted for authentication, provide the generated MCP API key.

Expected result:

```text
VS Code should discover the seven Logic Apps workflows as MCP tools.
```

If VS Code shows `Dynamic Client Registration not supported`, cancel that dialog. That popup means VS Code is trying OAuth. Confirm the Azure MCP server authentication method is `Key-based`, then start the server from `.vscode/mcp.json` so the `X-API-Key` header is sent with the generated key.

This is preferred over wiring each workflow callback URL directly into the agent because the MCP server becomes the tool exposure layer.

## Cost Control

This is a disposable learning deployment. WS1 can continue to cost while the resources exist.

When not testing, delete:

- `la-sysint-enterprise-integration-eus`
- `asp-sysint-enterprise-integration-eus`
- `stsysintintegeus001`

Delete script:

```powershell
.\infra\scripts\destroy-dev.ps1
```

The script asks you to type `DELETE` before removing resources.

## Files Created Or Updated

Infrastructure:

```text
infra/main.bicep
infra/modules/logicapp.bicep
infra/modules/storage.bicep
infra/parameters.dev.json
infra/scripts/deploy-dev.ps1
infra/scripts/destroy-dev.ps1
infra/scripts/publish-logicapps.ps1
```

Logic Apps publish hygiene:

```text
logicapps/standard-app/.funcignore
```

Step notes:

```text
development/step16/step-16a-azure-logic-apps-deployment-plan.md
development/step16/step-16b-azure-bicep-validation.md
development/step16/step-16c-azure-logic-apps-infra-deployment.md
development/step16/step-16d-publish-azure-workflows.md
development/step16/step-16e-mcp-tool-description-metadata.md
development/step16/step-16f-node-runtime-upgrade.md
development/step16/step-16g-enable-logic-apps-mcp-server.md
```
