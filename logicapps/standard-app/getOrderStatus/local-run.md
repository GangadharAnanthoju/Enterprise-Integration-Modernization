# getOrderStatus Local Run Notes

## Request Body

Use:

```json
{
  "order_id": "ORD-1001"
}
```

The same payload is stored in:

```text
getOrderStatus/sample-request.json
```

## Expected Success Response

```json
{
  "orderNumber": "4500098123",
  "requestedOrderId": "ORD-1001",
  "status": "In Transit",
  "estimatedDeliveryDate": "2026-05-21",
  "delayRisk": "Medium",
  "correlationId": "<workflow-run-or-request-correlation>"
}
```

## Expected Missing Entity Response

If `order_id` is missing or empty, the workflow returns HTTP 400:

```json
{
  "error": "missing_required_entity",
  "message": "The getOrderStatus workflow requires order_id."
}
```

## MCP Connection Plan

After the local runtime provides a trigger URL, use that URL as:

```env
MCP_SERVER_URL=http://localhost:7071/api/<generated-getOrderStatus-route>
```

Then the remote MCP path can call the local Logic App:

```text
Agent -> RemoteMcpHttpClient -> local getOrderStatus workflow
```
