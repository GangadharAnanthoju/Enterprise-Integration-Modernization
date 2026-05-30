# Step 10B - Connect Remote MCP Mode To Local Logic Apps

## Goal

Use the local Logic Apps Standard runtime as the remote MCP backend before deploying anything to Azure.

This keeps the architecture realistic while avoiding the daily cost of a hosted Logic Apps Standard `WS1` plan.

## What Changed

- Updated the local `getOrderStatus` workflow to accept the governed MCP HTTP envelope.
- Updated the `getOrderStatus` sample request to match the agent's remote MCP client.
- Documented how to run the local Logic Apps project and point the agent at the local workflow URL.

## Local Architecture

```text
User
  -> FastAPI /agent/chat
  -> Agent planned action
  -> MCP request builder
  -> RemoteMcpHttpClient
  -> Local Logic Apps Standard getOrderStatus HTTP trigger
  -> Normalized MCP execution result
```

## MCP Envelope Sent By The Agent

The agent remote MCP client sends this shape:

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

The workflow reads `payload.order_id` and returns the normalized remote MCP shape:

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

## Local Run Steps

Open the Logic Apps workspace in a separate VS Code window:

```text
C:\Data_AI\projects\Enterprise-Integration-Modernization\logicapps\standard-app\Enterprise-Integration-LogicApps.code-workspace
```

Then:

1. Start Azurite if your local runtime uses `UseDevelopmentStorage=true`.
2. Start the Logic Apps runtime from the VS Code extension or from a terminal in `logicapps/standard-app`:

   ```powershell
   func start
   ```

3. Copy the generated local HTTP trigger URL for `getOrderStatus`.
4. Put that URL into the agent environment. You can use either the fallback endpoint or the preferred per-tool endpoint:

   ```env
   MOCK_MCP=false
   MCP_EXECUTION_MODE=remote
   MCP_TOOL_ENDPOINT_GET_ORDER_STATUS=http://localhost:7071/api/<generated-getOrderStatus-route>
   MCP_API_KEY=
   ```

5. Start the FastAPI agent service from the `agent` folder:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   $env:PYTHONPATH="src"
   uvicorn src.main:app --reload --port 8001
   ```

6. Call `/agent/chat` with `simulate_when_ready=true` and a message like:

   ```json
   {
     "user_message": "Check order ORD-1001",
     "simulate_when_ready": true
   }
   ```

## First-Step Scope

This step connects one workflow, `getOrderStatus`, end to end.

The project supports both a fallback `MCP_SERVER_URL` and per-tool endpoint settings. For Logic Apps-as-tools, prefer per-tool settings so each workflow can be called as its own approved MCP tool:

```env
MCP_TOOL_ENDPOINT_GET_ORDER_STATUS=<getOrderStatus callback URL>
MCP_TOOL_ENDPOINT_CHECK_SHIPMENT_STATUS=<checkShipmentStatus callback URL>
MCP_TOOL_ENDPOINT_VALIDATE_INVOICE=<validateInvoice callback URL>
```

A later step can add one of these broader production patterns:

- a local Logic Apps dispatcher workflow that routes by `tool_name`
- a real MCP server facade in front of Logic Apps

For learning, starting with one read-only workflow is the cleanest way to prove the remote path without adding Azure cost.

## Interview Explanation

Step 10B proves the cloud deployment path locally. The agent is no longer limited to mock sample files; it can use the same remote HTTP MCP client that will later call Azure. The backend is a local Logic Apps Standard workflow, so the team can validate contracts, correlation IDs, workflow behavior, and response normalization before paying for hosted infrastructure.

## Local Authentication Note

For local Logic Apps Standard callback URLs, leave `MCP_API_KEY` empty.

The local callback URL already includes a `sig` query-string token. If `MCP_API_KEY` is set, the agent sends an `Authorization: Bearer ...` header, which can cause the local Logic Apps runtime to reject the request.
