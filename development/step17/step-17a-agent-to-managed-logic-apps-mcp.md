# Step 17A - Connect Agent To Managed Logic Apps MCP Server

## Goal

Move the Python agent remote execution path from direct workflow callback URLs to the managed Logic Apps MCP server endpoint.

## Managed MCP Endpoint

```text
https://la-sysint-enterprise-integration-eus.azurewebsites.net/api/mcpservers/enterpriseintegrationmcp/mcp
```

## Why This Matters

Earlier remote mode used a direct HTTP envelope that worked for workflow callback URLs.

The managed Logic Apps MCP server uses the Model Context Protocol over Streamable HTTP:

```text
initialize
notifications/initialized
tools/call
```

This means the agent should behave like a real MCP client instead of posting directly to a single workflow callback URL.

## Code Updated

```text
agent/src/mcp/remote.py
agent/tests/test_mcp_executors.py
```

## Runtime Behavior

The remote client now:

1. Sends an MCP `initialize` request.
2. Preserves `Mcp-Session-Id` when the server returns one.
3. Sends `notifications/initialized`.
4. Calls the selected tool with `tools/call`.
5. Sends the Logic Apps MCP API key using `X-API-Key`.
6. Normalizes MCP tool content into the existing agent simulation result shape.

## Local Configuration

Use:

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

Do not commit `agent/.env`.

## Verification

Focused tests:

```powershell
cd agent
.\.venv\Scripts\python.exe -m pytest tests\test_mcp_executors.py tests\test_mcp_request_builder.py tests\test_config_validation.py
```

When `agent/.env` is pointed at Azure remote MCP, run tests with mock-mode overrides:

```powershell
cd agent
$env:MOCK_MCP='true'
$env:MCP_EXECUTION_MODE='mock'
$env:MCP_SERVER_URL=''
$env:MCP_API_KEY=''
.\.venv\Scripts\python.exe -m pytest
```

Result:

```text
Focused MCP tests: 25 passed
Full suite with mock-mode overrides: 137 passed
```

## Learning Note

For interview explanation:

```text
We moved from direct workflow callback integration to a managed MCP protocol client. The agent now follows the MCP lifecycle and calls Logic Apps workflows through tools/call, while the FastAPI layer still enforces risk policy, approval gates, and audit boundaries.
```
