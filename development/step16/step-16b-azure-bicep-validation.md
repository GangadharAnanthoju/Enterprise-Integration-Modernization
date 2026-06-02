# Step 16B - Azure Bicep Validation

## Goal

Validate the disposable Logic Apps Standard Bicep deployment before creating Azure resources.

No resources are deployed in this step.

## Local Compile Validation

Command:

```powershell
bicep build infra\main.bicep
```

Result:

```text
Passed
```

The template compiles locally.

## Azure Deployment Validation

### East US

Command:

```powershell
az deployment group validate `
  --resource-group rg-sysint-enterprise-integration-eus `
  --template-file infra\main.bicep `
  --parameters @infra\parameters.dev.json `
  --parameters location=eastus
```

Result:

```text
Blocked by Azure quota
```

Azure returned:

```text
SubscriptionIsOverQuotaForSku
Location: East US
Current Limit (Total VMs): 0
Current Usage: 0
Amount required for this deployment (Total VMs): 1
Minimum new limit required: 1
```

### Sweden Central

Command:

```powershell
az deployment group validate `
  --resource-group rg-sysint-enterprise-integration-eus `
  --template-file infra\main.bicep `
  --parameters @infra\parameters.dev.json `
  --parameters location=swedencentral
```

Result:

```text
Passed
```

Azure validation reached preflight successfully for:

```text
location=swedencentral
logicAppName=la-sysint-enterprise-integration-eus
appServicePlanName=asp-sysint-enterprise-integration-eus
storageAccountName=stsysintintegeus001
```

## Meaning

The Bicep structure is valid. East US cannot currently deploy the selected WS1 Logic Apps Standard plan because this subscription has zero VM quota there. Sweden Central passed validation with the same disposable WS1 deployment shape.

## Cost And Deployment Decision

This is actually a useful safety checkpoint.

The project remains on the cost-safe local Logic Apps path until one of these options is approved:

| Option | Impact |
|---|---|
| Request quota of `1` for East US | Allows WS1 deployment in the original intended region |
| Deploy in Sweden Central | Passed validation; fastest path for a short-lived learning deployment |
| Continue local-only Logic Apps | No Azure hosting cost |
| Rebuild as Logic Apps Consumption workflows | More usage-based, but different project shape from local Standard |

## Current Recommendation

Do not deploy until explicitly approved.

If you want the fastest Azure test path, use Sweden Central and delete the resources after testing. If region alignment matters more than speed, request East US quota first.

## Interview Explanation

Before provisioning, I ran both local Bicep compile validation and Azure preflight validation. Azure blocked the Workflow Standard deployment in East US because the subscription had zero VM quota there, so I tested Sweden Central and validation passed. No resources were created. This shows cost-aware and quota-aware cloud deployment discipline instead of blindly provisioning infrastructure.
