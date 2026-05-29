# Step 10D - Add checkShipmentStatus Local MCP Workflow

## Goal

Convert `checkShipmentStatus` to the same governed MCP envelope used by `getOrderStatus`.

This gives the project a second local Logic Apps workflow that can be called as its own MCP tool endpoint.

## What Changed

- Updated `checkShipmentStatus/workflow.json` in both Logic Apps folders.
- Updated sample request files to use the MCP envelope.
- Expanded the workflow README with request and response examples.

## MCP Request Shape

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

## MCP Response Shape

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

## Local Agent Configuration

Once the local callback URL is available:

```env
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_TOOL_ENDPOINT_CHECK_SHIPMENT_STATUS=<checkShipmentStatus callback URL>
MCP_API_KEY=
```

For local Logic Apps callback URLs, keep `MCP_API_KEY` empty because the URL already includes its own `sig` token.

## Interview Explanation

Step 10D proves the per-tool endpoint pattern beyond the first order-status workflow. The agent can now treat shipment status as a separate approved MCP tool with its own Logic Apps workflow, request contract, response contract, and endpoint setting.
