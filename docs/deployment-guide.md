# Deployment Guide

This project starts in local mock mode, then deploys Azure infrastructure, Logic Apps MCP workflows, Functions, and the agent API. Foundry setup is treated as a required platform baseline, not an optional add-on.

For the exact Logic Apps Standard deployment commands used in this project, see:

```text
docs/logic-apps-azure-deployment-guide.md
```

## Deployment Order

1. Verify package and SDK versions for Microsoft Agent Framework and Foundry.
2. Create or select the Microsoft Foundry project and model deployment.
3. Deploy shared Azure infrastructure from `infra/`.
4. Deploy Azure Functions helpers from `functions/`.
5. Deploy Logic Apps Standard workflows from `logicapps/workflows/`.
6. Configure the remote MCP endpoint and authentication.
7. Deploy the FastAPI agent service from `agent/`.
8. Run smoke tests and Foundry evaluation baselines.

## Required Configuration

Key settings are listed in `.env.example`:

- Foundry project endpoint and deployment names.
- MCP server URL and API key or auth configuration.
- `MOCK_MCP` for local mode.
- Application Insights connection string.

## Release Readiness

Before demo or deployment:

- `foundry/governance/release-checklist.md` is complete.
- Tool catalog matches Logic Apps workflow names.
- High-risk tools require approval.
- Local tests pass.
- Foundry evaluation baseline passes.
- Application Insights receives correlated traces.
