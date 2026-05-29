# checkShipmentStatus

Returns shipment status and delay risk for an order.

## MCP Tool Contract

| Field | Value |
|---|---|
| Tool name | `checkShipmentStatus` |
| Logic Apps workflow | `checkShipmentStatus` |
| Risk level | Low |
| Approval required | No |
| Required entity | `shipment_id` |
| Method | `POST` |
| Response type | JSON |

## Request

The agent sends a governed MCP payload:

```json
{
  "server_name": "logic-apps-standard-mcp",
  "tool_name": "checkShipmentStatus",
  "correlation_id": "local-corr-ship-001",
  "payload": {
    "shipment_id": "SHIP-3001"
  },
  "timeout_seconds": 30
}
```

The Logic Apps workflow maps `payload.shipment_id` to the backend shipment lookup key.

## Response

```json
{
  "status": "completed",
  "result": {
    "requestedShipmentId": "SHIP-3001",
    "orderNumber": "4500098123",
    "shipmentStatus": "In Transit",
    "eta": "2026-05-21",
    "delayRisk": "Medium",
    "correlationId": "local-corr-ship-001"
  },
  "message": "Remote MCP execution completed by local Logic Apps workflow."
}
```

## Designer-Friendly Project Copy

A Logic Apps Standard project copy is available at:

```text
logicapps/standard-app/checkShipmentStatus/workflow.json
```
