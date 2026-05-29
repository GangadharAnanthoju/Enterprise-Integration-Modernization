# sendSupplierNotification

Sends a supplier notification after approval.

## MCP Tool Contract

| Field | Value |
|---|---|
| Tool name | `sendSupplierNotification` |
| Logic Apps workflow | `sendSupplierNotification` |
| Risk level | High |
| Approval required | Yes |
| Required entity | `shipment_id` |
| Method | `POST` |
| Response type | JSON |

## Request

The approved execution path sends a governed MCP payload:

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

The workflow maps `payload.shipment_id` to the supplier notification event.

## Response

```json
{
  "status": "completed",
  "result": {
    "notificationId": "NOTIF-1001",
    "requestedShipmentId": "SHIP-3001",
    "status": "Sent",
    "correlationId": "local-corr-supplier-001"
  },
  "message": "Remote MCP execution completed by local Logic Apps workflow."
}
```

## Governance Note

This workflow is high risk. The agent chat path must create an approval request first; direct execution should happen only through the approved action endpoint.
