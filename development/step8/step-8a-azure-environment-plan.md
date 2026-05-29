# Step 8A: Azure Environment Configuration Plan

## Goal

Plan how the project will move from safe local mock mode to real Azure-backed remote MCP execution.

This step does not call Azure and does not require real secrets. It defines the environment strategy first so future remote execution, Foundry runtime, and observability work can be configured safely.

## Guiding Rules

- Local development stays in mock mode by default.
- Remote execution is enabled only through environment variables.
- Secrets are never committed.
- API diagnostics can show whether a secret is configured, but never the secret value.
- Foundry settings stay separate from MCP execution settings.
- Key Vault can replace local `.env` secrets later.

## Configuration Groups

### Local Development

Used for learning, tests, and safe demos.

```env
MOCK_MCP=true
MCP_EXECUTION_MODE=mock
MCP_SERVER_NAME=logic-apps-standard-mcp
MCP_SERVER_URL=
MCP_API_KEY=
MCP_TIMEOUT_SECONDS=30
```

### Remote MCP Execution

Used when a real Logic Apps Standard MCP endpoint is available.

```env
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_SERVER_NAME=logic-apps-standard-mcp
MCP_SERVER_URL=https://your-logic-app-or-mcp-endpoint
MCP_API_KEY=your-secret-value
MCP_TIMEOUT_SECONDS=30
```

### Foundry Runtime

Used later when the agent adapter points to Microsoft Foundry / Agent Framework.

```env
FOUNDRY_PROJECT_ENDPOINT=https://your-foundry-project-endpoint
MODEL_DEPLOYMENT_NAME=your-model-deployment
FOUNDRY_AGENT_NAME=enterprise-integration-agent
FOUNDRY_EVAL_DATASET_NAME=enterprise-mcp-regression
```

### Observability

Used later for Application Insights and Azure Monitor export.

```env
APPLICATIONINSIGHTS_CONNECTION_STRING=your-app-insights-connection-string
LOG_ANALYTICS_WORKSPACE_ID=your-log-analytics-workspace-id
```

## Step 8 Roadmap

| Step | Purpose |
|---|---|
| 8A | Document the Azure environment plan |
| 8B | Add `.env.example` for local and remote modes |
| 8C | Add environment validation checks |
| 8D | Add readiness checks for remote MCP settings |
| 8E | Add Foundry and observability environment notes |
| 8F | Finish Step 8 with tests and docs |

## Why This Matters

The project already has a tested remote MCP HTTP client path. Step 8 makes sure that real connectivity is turned on deliberately, with environment variables and safe diagnostics, instead of hardcoded endpoints or secrets.

## Interview Talking Point

Step 8 shows production-minded configuration management: mock mode by default, remote mode by explicit environment settings, and no secret exposure through API responses or audit logs.
