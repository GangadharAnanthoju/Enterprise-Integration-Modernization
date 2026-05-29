# Step 10A - Azure Resource Review Before Deployment

## Goal

Review the Azure resources needed to deploy the local Logic Apps Standard workflows before creating anything in Azure.

This is intentionally a review step only. No Azure resources are deployed in this step.

## Deployment Target

| Setting | Value |
|---|---|
| Azure region | `eastus` |
| Resource group | `rg-sysint-enterprise-integration-eus` |
| Logic App name provided | `la-sysint-enterprise-integraion-eus` |
| Cost posture | Lowest practical Logic Apps Standard setup for a learning project |

## Name Review

The Logic App name provided is:

`la-sysint-enterprise-integraion-eus`

That name appears to contain a spelling difference: `integraion` instead of `integration`.

Before deployment, confirm whether to use the name exactly as provided or the corrected name:

`la-sysint-enterprise-integration-eus`

## Required Resources For First Azure Deployment

These are the minimum resources needed to deploy the Logic Apps Standard workflows to Azure.

| Resource | Proposed name | Required? | Why it is needed |
|---|---|---:|---|
| Resource group | `rg-sysint-enterprise-integration-eus` | Yes | Existing container for all project resources |
| Logic Apps Standard app | Pending name confirmation | Yes | Hosts the enterprise workflow endpoints |
| App Service plan | `asp-sysint-enterprise-integration-eus` | Yes | Required compute plan for Logic Apps Standard |
| Storage account | `stsysintintegeus001` or another available name | Yes | Required by Logic Apps Standard runtime for workflow state and host files |

## Low-Cost Plan Choice

For this learning project, use the smallest practical Logic Apps Standard workflow plan:

| Setting | Proposed value |
|---|---|
| Plan type | Workflow Standard |
| SKU | `WS1` |
| Scale posture | Start small; scale later only if needed |

This is not the same as Logic Apps Consumption. We are using Logic Apps Standard because it supports the local project structure and designer workflow we prepared in Step 9.

## Deferred Resources

These resources are useful later, but should not be created in the first deployment unless there is a specific reason.

| Resource | Status | Reason |
|---|---|---|
| Application Insights | Defer | Helpful for monitoring, but can add cost and is not required for first workflow deployment |
| Log Analytics workspace | Defer | Usually paired with App Insights; add when we start Azure observability validation |
| Key Vault | Defer | Important for production secrets, but first deployment can use app settings while we validate the workflow path |
| API Management | Defer | Useful for enterprise API governance, but not required before MCP exposure is proven |
| Service Bus | Defer | Useful for async integration patterns, but not required for current HTTP-triggered workflows |
| Function App | Defer | Not needed because Logic Apps workflows are the backend execution layer for this step |

## What Will Not Happen In 10A

- No Azure CLI deployment.
- No resource creation.
- No Bicep deployment.
- No workflow publish.
- No secrets added.

## Approval Checkpoint Before 10B

Before Step 10B, confirm:

1. Use the existing resource group: `rg-sysint-enterprise-integration-eus`.
2. Use the provided Logic App name exactly, or correct it to `la-sysint-enterprise-integration-eus`.
3. Use a low-cost Logic Apps Standard plan with `WS1`.
4. Create only required resources first: Logic App Standard app, App Service plan, and storage account.
5. Defer App Insights, Log Analytics, Key Vault, API Management, Service Bus, and Function App.

## Interview Explanation

Step 10A is the cloud deployment governance checkpoint. Instead of jumping straight to Azure, we identified the minimum resources required for Logic Apps Standard, separated required resources from optional enterprise platform resources, and created an approval point before deployment. This matches enterprise change-control behavior: review cost, names, region, and operational scope before provisioning.
