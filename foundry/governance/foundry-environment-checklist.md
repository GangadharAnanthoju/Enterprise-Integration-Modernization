# Foundry Environment Checklist

This checklist captures the non-secret Foundry environment values for the enterprise integration agent.

Do not store client secrets, API keys, Logic Apps callback signatures, or connection-string secrets in this file.

## Confirmed Values

| Setting | Value |
|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | `https://ms-foundry-sysint-02.services.ai.azure.com/api/projects/proj-sysint-01` |
| `MODEL_DEPLOYMENT_NAME` | `gpt-4.1-mini` |
| `FOUNDRY_AGENT_NAME` | `enterprise-integration-agent` |
| `FOUNDRY_EVAL_DATASET_NAME` | `enterprise-mcp-regression` |
| `AZURE_TENANT_ID` | `8a79bab5-15fc-42b2-8a7d-bbb5d939fb4c` |
| `AZURE_SUBSCRIPTION_ID` | `d835f9fb-e4f6-4ffe-9740-e32ebdef91ff` |
| `AZURE_RESOURCE_GROUP` | `rg-sysint-ms-foundry` |
| `AZURE_AI_ACCOUNT_NAME` | `ms-foundry-sysint-02` |
| `AZURE_AI_PROJECT_NAME` | `proj-sysint-01` |
| Foundry account location | `eastus` |
| Foundry project location | `eastus` |

## CLI Observations

Azure CLI returned these resources in `rg-sysint-ms-foundry`:

| Name | Type | Location |
|---|---|---|
| `ms-foundry-sysint-02` | `Microsoft.CognitiveServices/accounts` | `eastus` |
| `ms-foundry-sysint-02/proj-sysint-01` | `Microsoft.CognitiveServices/accounts/projects` | `eastus` |

Azure CLI also showed additional `swedencentral` resources in the same resource group:

| Name | Type | Location |
|---|---|---|
| `proj-tools-01-resource` | `Microsoft.CognitiveServices/accounts` | `swedencentral` |
| `proj-tools-01-resource/proj-tools-01` | `Microsoft.CognitiveServices/accounts/projects` | `swedencentral` |

For this project, use `ms-foundry-sysint-02/proj-sysint-01`.

## Confirmed Model Deployments

| Deployment | Model | Version | SKU | Capacity |
|---|---|---|---|---|
| `gpt-4.1-mini` | `gpt-4.1-mini` | `2025-04-14` | `GlobalStandard` | `10` |
| `gpt-4.1` | `gpt-4.1` | `2025-04-14` | `GlobalStandard` | `500` |
| `text-embedding-3-small` | `text-embedding-3-small` | `1` | `Standard` | `120` |

Recommended starting model for this project: `gpt-4.1-mini`.

## Local `agent/.env` Values To Set

```env
FOUNDRY_PROJECT_ENDPOINT=https://ms-foundry-sysint-02.services.ai.azure.com/api/projects/proj-sysint-01
MODEL_DEPLOYMENT_NAME=gpt-4.1-mini
FOUNDRY_AGENT_NAME=enterprise-integration-agent
FOUNDRY_EVAL_DATASET_NAME=enterprise-mcp-regression
AZURE_TENANT_ID=8a79bab5-15fc-42b2-8a7d-bbb5d939fb4c
AZURE_SUBSCRIPTION_ID=d835f9fb-e4f6-4ffe-9740-e32ebdef91ff
AZURE_RESOURCE_GROUP=rg-sysint-ms-foundry
AZURE_AI_ACCOUNT_NAME=ms-foundry-sysint-02
AZURE_AI_PROJECT_NAME=proj-sysint-01
```

## Still Open

- Confirm whether Application Insights should use an existing shared resource or stay unset for now.
- Confirm whether Key Vault should be used before live tool registration.
- Confirm the first Foundry agent creation method: portal, SDK, or CLI-supported workflow.
