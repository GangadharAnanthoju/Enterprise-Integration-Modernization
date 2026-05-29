# queryIntegrationRunStatus

Returns integration workflow run status for support troubleshooting.

## MCP Tool Contract

| Field | Value |
|---|---|
| Tool name | `queryIntegrationRunStatus` |
| Logic Apps workflow | `queryIntegrationRunStatus` |
| Risk level | Low |
| Approval required | No |
| Required entity | `correlation_id` |
| Method | `POST` |
| Response type | JSON |

## Request

The agent sends a governed MCP payload:

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

The Logic Apps workflow maps `payload.correlation_id` to the backend integration run lookup key.

## Response

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

## Designer-Friendly Project Copy

A Logic Apps Standard project copy is available at:

```text
logicapps/standard-app/queryIntegrationRunStatus/workflow.json
```
