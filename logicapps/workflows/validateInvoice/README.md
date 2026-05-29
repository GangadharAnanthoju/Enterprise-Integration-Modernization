# validateInvoice

Validates invoice details against purchase order and vendor data.

## MCP Tool Contract

| Field | Value |
|---|---|
| Tool name | `validateInvoice` |
| Logic Apps workflow | `validateInvoice` |
| Risk level | Low |
| Approval required | No |
| Required entity | `invoice_id` |
| Method | `POST` |
| Response type | JSON |

## Request

The agent sends a governed MCP payload:

```json
{
  "server_name": "logic-apps-standard-mcp",
  "tool_name": "validateInvoice",
  "correlation_id": "local-corr-invoice-001",
  "payload": {
    "invoice_id": "INV-2001"
  },
  "timeout_seconds": 30
}
```

The Logic Apps workflow maps `payload.invoice_id` to the backend invoice validation key.

## Response

```json
{
  "status": "completed",
  "result": {
    "invoiceNumber": "INV-2001",
    "validationStatus": "Passed",
    "matchedPO": true,
    "taxValidation": "Passed",
    "requiresApproval": false,
    "correlationId": "local-corr-invoice-001"
  },
  "message": "Remote MCP execution completed by local Logic Apps workflow."
}
```

## Designer-Friendly Project Copy

A Logic Apps Standard project copy is available at:

```text
logicapps/standard-app/validateInvoice/workflow.json
```
