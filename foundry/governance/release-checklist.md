# Release Checklist

- Verify current Microsoft Agent Framework package and API guidance.
- Verify Foundry SDK and hosted agent runtime guidance.
- Confirm the agent definition points to the current instruction file.
- Confirm MAF registration preflight passes before live Foundry creation.
- Confirm Foundry agent version `enterprise-integration-agent:2` is active before structured planning work.
- Confirm Foundry agent version `enterprise-integration-agent:2` responds with parseable JSON for a safe test message.
- Confirm publishing is deferred until invocation and evaluations pass.
- Confirm Foundry-facing tool registration metadata matches the approved MCP registry.
- Run unit and contract tests.
- Confirm high-risk tools require approval.
