# getOrderStatus Local Run Notes

## Request Body

Use:

```json
{
  "server_name": "logic-apps-standard-mcp",
  "tool_name": "getOrderStatus",
  "correlation_id": "local-corr-001",
  "payload": {
    "order_id": "ORD-1001"
  },
  "timeout_seconds": 30
}
```

The same payload is stored in:

```text
getOrderStatus/sample-request.json
```

## Expected Success Response

```json
{
  "status": "completed",
  "result": {
    "orderNumber": "4500098123",
    "requestedOrderId": "ORD-1001",
    "status": "In Transit",
    "estimatedDeliveryDate": "2026-05-21",
    "delayRisk": "Medium",
    "correlationId": "local-corr-001"
  },
  "message": "Remote MCP execution completed by local Logic Apps workflow."
}
```

## Expected Missing Entity Response

If `tool_name` is not `getOrderStatus`, or `payload.order_id` is missing or empty, the workflow returns HTTP 400:

```json
{
  "status": "failed",
  "error": "invalid_mcp_request",
  "message": "The getOrderStatus workflow requires tool_name=getOrderStatus and payload.order_id."
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

Leave `MCP_API_KEY` empty for local Logic Apps callback URLs. The callback URL already includes a `sig` query-string token.

```env
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_TOOL_ENDPOINT_GET_ORDER_STATUS=http://localhost:7071/api/<generated-getOrderStatus-route>
MCP_API_KEY=
```
