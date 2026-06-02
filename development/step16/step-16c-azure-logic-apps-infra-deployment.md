# Step 16C - Azure Logic Apps Infrastructure Deployment

## Goal

Deploy the minimum disposable Azure infrastructure for the Logic Apps Standard MCP workflow host.

This step deploys infrastructure only. Workflow code publishing is a separate later step.

## Deployment Command

```powershell
az deployment group create `
  --resource-group rg-sysint-enterprise-integration-eus `
  --template-file infra\main.bicep `
  --parameters @infra\parameters.dev.json `
  --parameters location=swedencentral
```

## Deployment Result

Result:

```text
Succeeded
```

Deployment duration:

```text
PT1M20.4418857S
```

## Deployed Resources

| Resource | Name | Region | Status |
|---|---|---|---|
| Logic App Standard app | `la-sysint-enterprise-integration-eus` | Sweden Central | Running |
| Workflow Standard plan | `asp-sysint-enterprise-integration-eus` | Sweden Central | `WS1` |
| Storage account | `stsysintintegeus001` | Sweden Central | `Standard_LRS` |

Logic App default host:

```text
la-sysint-enterprise-integration-eus.azurewebsites.net
```

## Cost Posture

This is a disposable learning deployment.

When not using it, delete:

- Logic App Standard app
- Workflow Standard plan
- Storage account

The helper script is:

```text
infra/scripts/destroy-dev.ps1
```

## What Is Still Pending

The Azure host exists, but workflows still need to be published from:

```text
logicapps/standard-app
```

After workflow publishing, we still need to:

- fetch Azure workflow callback URLs
- update MCP endpoint settings
- run `/agent/chat` against Azure-hosted Logic Apps
- delete resources when finished testing

## Interview Explanation

I deployed only the minimum Logic Apps Standard infrastructure needed for a learning MCP backend: a WS1 Workflow Standard plan, a Logic App Standard app, and a Standard_LRS storage account. I intentionally deferred App Insights, APIM, Key Vault, and Log Analytics to keep cost and complexity low for the first cloud validation.
