# Step 10F - Add queryIntegrationRunStatus Local MCP Workflow

## Goal

Convert `queryIntegrationRunStatus` to the governed MCP envelope pattern.

This completes the low-risk read-only local Logic Apps workflow group.

## What Changed

- Updated `queryIntegrationRunStatus/workflow.json` in both Logic Apps folders.
- Updated sample request files to use the MCP envelope.
- Expanded the workflow README with request and response examples.

## MCP Request Shape

```json
{
  "server_name": "logic-apps-standard-mcp",
  "tool_name": "queryIntegrationRunStatus",
  "correlation_id": "local-corr-run-001",
  "payload": {
    "correlation_id": "demo-corr-001"
  },
  "timeout_seconds": 30
}
```

## MCP Response Shape

```json
{
  "status": "completed",
  "result": {
    "runId": "RUN-90001",
    "requestedCorrelationId": "demo-corr-001",
    "status": "Failed",
    "errorCategory": "BACKEND_TIMEOUT",
    "correlationId": "local-corr-run-001"
  },
  "message": "Remote MCP execution completed by local Logic Apps workflow."
}
```

## Local Agent Configuration

Once the local callback URL is available:

```env
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_TOOL_ENDPOINT_QUERY_INTEGRATION_RUN_STATUS=<queryIntegrationRunStatus callback URL>
MCP_API_KEY=
```

## Interview Explanation

Step 10F adds troubleshooting and operations lookup to the same local MCP pattern. The agent can now use Logic Apps for low-risk business lookups and integration-support lookups through the same governed execution path.
