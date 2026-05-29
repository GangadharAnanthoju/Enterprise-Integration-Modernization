# Step 10E - Add validateInvoice Local MCP Workflow

## Goal

Convert `validateInvoice` to the governed MCP envelope pattern.

This gives the project a third low-risk local Logic Apps workflow that can be called through per-tool MCP endpoint mapping.

## What Changed

- Updated `validateInvoice/workflow.json` in both Logic Apps folders.
- Updated sample request files to use the MCP envelope.
- Expanded the workflow README with request and response examples.

## MCP Request Shape

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

## MCP Response Shape

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

## Local Agent Configuration

Once the local callback URL is available:

```env
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_TOOL_ENDPOINT_VALIDATE_INVOICE=<validateInvoice callback URL>
MCP_API_KEY=
```

## Interview Explanation

Step 10E adds invoice validation to the same local Logic Apps MCP pattern. At this point the project has multiple low-risk business tools running through the same governed agent-to-MCP-to-Logic-Apps path: order status, shipment status, and invoice validation.
