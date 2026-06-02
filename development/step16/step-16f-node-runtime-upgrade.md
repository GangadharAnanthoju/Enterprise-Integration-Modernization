# Step 16F - Node Runtime Upgrade

## Goal

Clear the Azure Portal warning that Node.js 18 LTS has reached end of life.

## Issue

Azure Portal showed:

```text
Upgrade your app to newer version as Node.js 18 LTS has reached EOL on 4/30/2025 and is no longer supported.
```

## Decision

Update the Logic App Standard app setting:

```text
WEBSITE_NODE_DEFAULT_VERSION=~24
```

Azure Functions runtime 4.x currently supports Node.js 22 and Node.js 24. Node.js 24 gives the longer support window.

## Commands

```powershell
az functionapp config appsettings set `
  --resource-group rg-sysint-enterprise-integration-eus `
  --name la-sysint-enterprise-integration-eus `
  --settings WEBSITE_NODE_DEFAULT_VERSION=~24
```

```powershell
az functionapp restart `
  --resource-group rg-sysint-enterprise-integration-eus `
  --name la-sysint-enterprise-integration-eus
```

## Verification

App setting:

```text
WEBSITE_NODE_DEFAULT_VERSION=~24
```

Workflow health after restart:

```text
checkShipmentStatus        Healthy  False
createApprovalRequest      Healthy  False
createServiceNowTicket     Healthy  False
getOrderStatus             Healthy  False
queryIntegrationRunStatus  Healthy  False
sendSupplierNotification   Healthy  False
validateInvoice            Healthy  False
```

## Source Update

The Bicep source was updated in:

```text
infra/modules/logicapp.bicep
```

Future deployments will use Node.js 24 by default.
