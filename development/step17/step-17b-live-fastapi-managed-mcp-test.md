# Step 17B - Live FastAPI Test Against Managed Logic Apps MCP

## Goal

Prove the full live path from FastAPI chat to Azure Logic Apps through the managed MCP server.

## Runtime Configuration

Local secret file:

```text
agent/.env
```

Required values:

```text
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_SERVER_URL=https://la-sysint-enterprise-integration-eus.azurewebsites.net/api/mcpservers/enterpriseintegrationmcp/mcp
MCP_API_KEY=<generated Logic Apps MCP API key>
```

## Test Command

Run from the `agent` folder:

```powershell
$env:PYTHONPATH='src'
@'
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
response = client.post('/agent/chat', json={
    'user_message': 'Check order ORD-1001',
    'correlation_id': 'live-mcp-corr-001',
    'simulate_when_ready': True,
})
print(response.status_code)
print(response.json())
'@ | .\.venv\Scripts\python.exe -
```

## Result

```text
HTTP_STATUS=200
CHAT_STATUS=completed
SELECTED_TOOL=getOrderStatus
TOOL_CALLED=True
APPROVAL_REQUIRED=False
SIM_STATUS=completed
SIM_MODE=remote
SIM_MESSAGE=Remote MCP execution completed by local Logic Apps workflow.
ORDER_NUMBER=4500098123
REQUESTED_ORDER_ID=ORD-1001
ORDER_STATUS=In Transit
```

## Confirmed Architecture

```text
FastAPI /agent/chat
  -> local governed planner
  -> risk policy allows low-risk getOrderStatus
  -> MCP Streamable HTTP initialize
  -> MCP tools/call
  -> Azure Logic Apps MCP server enterpriseintegrationmcp
  -> getOrderStatus workflow
  -> normalized agent chat response
```

## Learning Note

This proves the project has crossed from mock/local simulation into a real enterprise-style managed MCP execution path while keeping the FastAPI governance layer intact.
