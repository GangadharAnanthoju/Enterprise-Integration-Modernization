# getOrderStatus

Returns order status for a known order ID.

## MCP Tool Contract

| Field | Value |
|---|---|
| Tool name | `getOrderStatus` |
| Logic Apps workflow | `getOrderStatus` |
| Risk level | Low |
| Approval required | No |
| Required entity | `order_id` |
| Method | `POST` |
| Response type | JSON |

## Request

The agent sends a governed MCP payload:

```json
{
  "order_id": "ORD-1001"
}
```

The Logic Apps workflow can map `order_id` to the backend order lookup key.

## Response

```json
{
  "orderNumber": "4500098123",
  "status": "In Transit",
  "estimatedDeliveryDate": "2026-05-21",
  "delayRisk": "Medium",
  "correlationId": "abc-123"
}
```

## Backend Mapping

This workflow is planned as a read-only lookup. In a real implementation it can call an ERP order API, SQL stored procedure, SAP connector, or mocked backend service.

## Local Designer Shape

The local `workflow.json` is now configured with:

1. HTTP request trigger.
2. Request body schema requiring `order_id`.
3. `Validate_order_id` condition.
4. `Compose_order_status_response` action.
5. `Return_order_status` HTTP 200 response.
6. `Return_missing_order_id` HTTP 400 response.

This lets the workflow be inspected locally as an actual Logic Apps workflow design instead of an empty placeholder.

## Designer-Friendly Project Copy

A Logic Apps Standard project copy is available at:

```text
logicapps/standard-app/getOrderStatus/workflow.json
```

Open `logicapps/standard-app` directly in VS Code when you want the Logic Apps Standard extension to recognize the local project layout.
