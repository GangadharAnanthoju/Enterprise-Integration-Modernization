# createApprovalRequest

Creates an approval request for high-risk tool execution.

## MCP Tool Contract

| Field | Value |
|---|---|
| Tool name | `createApprovalRequest` |
| Logic Apps workflow | `createApprovalRequest` |
| Risk level | Medium |
| Approval required | No |
| Required entity | None in current contract |
| Method | `POST` |
| Response type | JSON |

## Request

The agent or governance layer sends a governed MCP payload:

```json
{
  "server_name": "logic-apps-standard-mcp",
  "tool_name": "createApprovalRequest",
  "correlation_id": "local-corr-approval-001",
  "payload": {
    "toolName": "sendSupplierNotification",
    "riskLevel": "High",
    "requestedBy": "demo-user",
    "businessJustification": "Supplier notification is required for delayed shipment handling."
  },
  "timeout_seconds": 30
}
```

The workflow represents the future enterprise approval task creation path.

## Response

```json
{
  "status": "completed",
  "result": {
    "approvalId": "APR-1001",
    "status": "Pending",
    "requestedTool": "sendSupplierNotification",
    "riskLevel": "High",
    "requestedBy": "demo-user",
    "businessJustification": "Supplier notification is required for delayed shipment handling.",
    "correlationId": "local-corr-approval-001"
  },
  "message": "Remote MCP execution completed by local Logic Apps workflow."
}
```
