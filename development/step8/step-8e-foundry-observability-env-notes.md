# Step 8E: Foundry And Observability Environment Notes

## Goal

Document how Foundry and observability settings fit into the environment plan.

These settings are warnings today because the project still uses local Foundry-style traces, local evaluations, and App Insights-style envelopes. They become required later when real Foundry runtime and telemetry export are connected.

## Foundry Settings

```env
FOUNDRY_PROJECT_ENDPOINT=https://your-foundry-project-endpoint
MODEL_DEPLOYMENT_NAME=your-model-deployment
FOUNDRY_AGENT_NAME=enterprise-integration-agent
FOUNDRY_EVAL_DATASET_NAME=enterprise-mcp-regression
```

## Observability Settings

```env
APPLICATIONINSIGHTS_CONNECTION_STRING=your-app-insights-connection-string
LOG_ANALYTICS_WORKSPACE_ID=your-log-analytics-workspace-id
```

## Why These Are Warnings Today

The current project can still demonstrate governance without live Foundry or App Insights:

- audit events are local
- Foundry trace records are projected locally
- App Insights event envelopes are projected locally
- evaluations run locally

When we connect real Foundry and Azure Monitor export, these checks can become stricter.

## Interview Talking Point

I treated Foundry and observability as first-class configuration groups, but kept them as warnings until the real hosted services are wired in. That lets local development remain productive while keeping the production path visible.
