# Step 12B - Foundry Environment Checklist

## Goal

Capture the real non-secret Foundry environment values and make the local environment validation aware of them.

## Added Files

```text
foundry/governance/foundry-environment-checklist.md
development/step12/step-12b-foundry-environment-checklist.md
```

## Updated Files

```text
agent/.env.example
agent/src/config.py
agent/src/config_validation.py
agent/tests/test_config_validation.py
development/azure-environment-setup.md
```

## Confirmed Foundry Values

```env
FOUNDRY_PROJECT_ENDPOINT=https://ms-foundry-sysint-02.services.ai.azure.com/api/projects/proj-sysint-01
MODEL_DEPLOYMENT_NAME=gpt-4.1-mini
FOUNDRY_AGENT_NAME=enterprise-integration-agent
FOUNDRY_EVAL_DATASET_NAME=enterprise-mcp-regression
AZURE_RESOURCE_GROUP=rg-sysint-ms-foundry
AZURE_AI_ACCOUNT_NAME=ms-foundry-sysint-02
AZURE_AI_PROJECT_NAME=proj-sysint-01
```

Azure CLI confirmed:

- subscription: `SysInt Inc`
- Foundry account: `ms-foundry-sysint-02`
- Foundry project: `proj-sysint-01`
- Foundry account/project region: `eastus`
- model deployment: `gpt-4.1-mini`

## What Changed In Validation

Environment validation now has a separate check:

```text
foundry_resource_context
```

It verifies that these non-secret Azure context values are configured:

- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `AZURE_AI_ACCOUNT_NAME`
- `AZURE_AI_PROJECT_NAME`

The existing `foundry_runtime` check still validates:

- `FOUNDRY_PROJECT_ENDPOINT`
- `MODEL_DEPLOYMENT_NAME`

## Why This Matters

Foundry runtime settings and Azure resource context are related, but not identical.

The runtime needs endpoint and model deployment to invoke an agent. Operational setup also needs tenant, subscription, resource group, account name, and project name for CLI lookup, RBAC, diagnostics, and future registration scripts.

## Interview Explanation

Before creating the real Foundry agent, I captured the non-secret Foundry environment values and added validation around them. This separates runtime settings from Azure resource context, avoids hardcoded cloud values in code, and makes future registration or diagnostics safer.
