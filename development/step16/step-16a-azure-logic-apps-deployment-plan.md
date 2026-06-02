# Step 16A - Azure Logic Apps Deployment Plan

## Goal

Prepare the local Logic Apps Standard project for a low-cost Azure deployment that can be deleted when not in use.

This step updates the deployment plan from the earlier review and confirms the final names.

## Confirmed Names

| Setting | Value |
|---|---|
| Resource group | `rg-sysint-enterprise-integration-eus` |
| Logic App Standard app | `la-sysint-enterprise-integration-eus` |
| Azure region | `swedencentral` |
| App Service plan | `asp-sysint-enterprise-integration-eus` |
| Storage account | `stsysintintegeus001` |

Earlier notes included the misspelled Logic App name `la-sysint-enterprise-integraion-eus`.
Step 16 uses the corrected name:

```text
la-sysint-enterprise-integration-eus
```

The resource names still include the `eus` suffix because they were already selected during the earlier East US plan. The actual deployment region is now `swedencentral` because East US quota is blocked for WS1.

## Cost Posture

Use the smallest practical Logic Apps Standard setup:

| Resource | Choice |
|---|---|
| Logic Apps hosting model | Standard / single-tenant |
| Plan SKU | `WS1` |
| Storage SKU | `Standard_LRS` |
| App Insights | Deferred |
| Log Analytics | Deferred |
| APIM | Deferred |
| Key Vault | Deferred |

Important cost note:

Logic Apps Standard runs on a hosting plan. Stopping the app is not the same as deleting the plan. For this learning project, the safest cost-control pattern is:

```text
create when needed
test the workflow
delete Logic App + plan + storage when done
recreate from Bicep later
```

## Minimum Resources

Only these resources are required for the first Azure deployment:

| Resource | Why |
|---|---|
| Logic App Standard app | Hosts the workflow endpoints |
| Workflow Standard plan `WS1` | Provides compute for the Standard app |
| Storage account | Required by the Functions/Logic Apps runtime |

## Deferred Enterprise Resources

These stay out of the first deployment to avoid cost and complexity:

- Application Insights
- Log Analytics
- API Management
- Key Vault
- Service Bus

They can be added later when we move from learning deployment to production hardening.

## Deployment Direction

Infrastructure is now represented in:

```text
infra/main.bicep
infra/modules/storage.bicep
infra/modules/logicapp.bicep
infra/parameters.dev.json
infra/scripts/deploy-dev.ps1
infra/scripts/destroy-dev.ps1
```

The Bicep deployment creates only the minimum disposable Azure resources.

## What This Step Does Not Do

This step does not publish workflow code yet.

The next step should handle workflow deployment from:

```text
logicapps/standard-app
```

to:

```text
la-sysint-enterprise-integration-eus
```

## Interview Explanation

For the Azure deployment phase, I separated resource provisioning from workflow publishing. First I created a minimal disposable Logic Apps Standard infrastructure path using WS1 and Standard_LRS storage, while deferring App Insights, APIM, Key Vault, and Log Analytics. This keeps cloud cost controlled while preserving the enterprise path to production hardening.
