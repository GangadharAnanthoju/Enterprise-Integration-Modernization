# Step 10G - Add High-Risk Local MCP Workflows

## Goal

Convert the two high-risk action workflows to the governed MCP envelope pattern:

- `sendSupplierNotification`
- `createServiceNowTicket`

These workflows are callable as local Logic Apps endpoints, but the agent chat path must still create approval requests before execution.

## What Changed

- Updated `sendSupplierNotification/workflow.json` in both Logic Apps folders.
- Updated `createServiceNowTicket/workflow.json` in both Logic Apps folders.
- Updated sample request files to use the MCP envelope.
- Expanded workflow READMEs with governance notes.

## sendSupplierNotification Request

```json
{
  "server_name": "logic-apps-standard-mcp",
  "tool_name": "sendSupplierNotification",
  "correlation_id": "local-corr-supplier-001",
  "payload": {
    "shipment_id": "SHIP-3001"
  },
  "timeout_seconds": 30
}
```

## createServiceNowTicket Request

```json
{
  "server_name": "logic-apps-standard-mcp",
  "tool_name": "createServiceNowTicket",
  "correlation_id": "local-corr-ticket-001",
  "payload": {
    "shortDescription": "Shipment delay detected",
    "assignmentGroup": "Integration Support"
  },
  "timeout_seconds": 30
}
```

## Local Agent Configuration

```env
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_TOOL_ENDPOINT_SEND_SUPPLIER_NOTIFICATION=<sendSupplierNotification callback URL>
MCP_TOOL_ENDPOINT_CREATE_SERVICENOW_TICKET=<createServiceNowTicket callback URL>
MCP_API_KEY=
```

## Governance Note

These workflows are high risk. The workflow endpoints can run locally for testing, but agent chat should not call them directly. The intended path is:

```text
Chat request
  -> planned high-risk action
  -> approval request
  -> approval decision
  -> approved execution endpoint
  -> Logic Apps workflow
```

## Interview Explanation

Step 10G proves that high-risk workflows can use the same MCP envelope and Logic Apps endpoint pattern while still preserving the approval boundary. The backend workflows are ready, but the agent policy remains the control point.
