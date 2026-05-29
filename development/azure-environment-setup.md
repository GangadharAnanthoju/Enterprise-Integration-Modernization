# Azure Environment Setup

This guide explains the environment variables used by the Enterprise Integration Modernization project.

The project is safe by default: it runs in mock MCP mode unless remote mode is explicitly configured.

## Create Your Local `.env`

Copy the committed template:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` locally. Do not commit `.env`.

## Local Mock Mode

Use this for development, tests, and demos that should not call real backend systems.

```env
MOCK_MCP=true
MCP_EXECUTION_MODE=mock
MCP_SERVER_NAME=logic-apps-standard-mcp
MCP_SERVER_URL=
MCP_API_KEY=
MCP_TIMEOUT_SECONDS=30
```

## Remote MCP Mode

Use this only when a real Logic Apps Standard MCP endpoint is available.

```env
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_SERVER_NAME=logic-apps-standard-mcp
MCP_SERVER_URL=https://your-logic-app-or-mcp-endpoint
MCP_API_KEY=your-secret-value
MCP_TIMEOUT_SECONDS=30
```

## Foundry Settings

These are placeholders for the future Foundry-hosted agent runtime.

```env
FOUNDRY_PROJECT_ENDPOINT=https://your-foundry-project-endpoint
MODEL_DEPLOYMENT_NAME=your-model-deployment
FOUNDRY_AGENT_NAME=enterprise-integration-agent
FOUNDRY_EVAL_DATASET_NAME=enterprise-mcp-regression
```

## Observability Settings

These are placeholders for future Azure Monitor / Application Insights export.

```env
APPLICATIONINSIGHTS_CONNECTION_STRING=your-app-insights-connection-string
LOG_ANALYTICS_WORKSPACE_ID=your-log-analytics-workspace-id
```

## Secret Handling

Do not commit real secrets.

For local development, use a private `.env` file. For Azure deployment, move secrets to Key Vault or managed platform configuration.

The API may expose safe booleans such as `api_key_configured`, but it must never return `MCP_API_KEY`.

## Current Safe Diagnostics

Use these endpoints to inspect runtime configuration without exposing secrets:

```text
GET /mcp/config
GET /mcp/executor
GET /operations/readiness
```

## Current Behavior

- Mock mode is the default.
- Remote mode uses the tested `httpx` MCP client.
- Remote mode still requires a valid endpoint and authentication value before it can call real infrastructure.
