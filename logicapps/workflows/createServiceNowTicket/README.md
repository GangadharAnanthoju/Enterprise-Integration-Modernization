# createServiceNowTicket

Creates a ServiceNow incident or support ticket.

## MCP Tool Contract

| Field | Value |
|---|---|
| Tool name | `createServiceNowTicket` |
| Logic Apps workflow | `createServiceNowTicket` |
| Risk level | High |
| Approval required | Yes |
| Required entity | None in current contract |
| Method | `POST` |
| Response type | JSON |

## Request

The approved execution path sends a governed MCP payload:

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

The workflow accepts optional `payload.shortDescription` and `payload.assignmentGroup` values, and defaults them when the approved execution payload is empty.

## Response

```json
{
  "status": "completed",
  "result": {
    "ticketNumber": "INC0012345",
    "status": "Created",
    "shortDescription": "Shipment delay detected",
    "assignmentGroup": "Integration Support",
    "correlationId": "local-corr-ticket-001"
  },
  "message": "Remote MCP execution completed by local Logic Apps workflow."
}
```

## Governance Note

This workflow is high risk. The agent chat path must create an approval request first; direct execution should happen only through the approved action endpoint.
