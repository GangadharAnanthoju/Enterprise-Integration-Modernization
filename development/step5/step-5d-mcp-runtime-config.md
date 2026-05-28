# Step 5D: MCP Runtime Configuration

## What We Built

We added runtime configuration for the MCP execution boundary.

The project still runs in mock mode by default, but the MCP layer now has a clear configuration shape for future remote Logic Apps Standard MCP connectivity.

## New Endpoint

```text
GET /mcp/config
```

Default response:

```json
{
  "mode": "mock",
  "server_name": "logic-apps-standard-mcp",
  "endpoint_configured": false,
  "timeout_seconds": 30
}
```

## Configuration Fields

| Setting | Default | Purpose |
|---|---|---|
| `mcp_execution_mode` | `mock` | Future mode selector for mock or remote execution. |
| `mcp_server_name` | `logic-apps-standard-mcp` | Logical MCP server name. |
| `mcp_server_url` | `None` | Future remote MCP endpoint URL. |
| `mcp_timeout_seconds` | `30` | Future remote MCP call timeout. |
| `mock_mcp` | `True` | Keeps local development safely in mock mode. |

## Why This Matters

This prepares the project for a real enterprise MCP server without hardcoding Azure URLs.

The execution boundary now has an explicit runtime mode:

```text
mock today
remote MCP later
```

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/config.py` | Adds MCP runtime settings. |
| `agent/src/mcp/schemas.py` | Adds `McpExecutionMode` and `McpServerConfig`. |
| `agent/src/mcp/client.py` | Adds `load_mcp_config`. |
| `agent/src/api/schemas.py` | Adds `McpServerConfigResponse`. |
| `agent/src/api/routes.py` | Adds `/mcp/config`. |
| `agent/tests/test_mcp_request_builder.py` | Tests default and remote config loading. |
| `agent/tests/test_agent_flow.py` | Tests the config endpoint. |

## Key Learning

Enterprise integrations should not hide runtime mode inside business logic.

The agent, MCP adapter, and operations teams should be able to tell whether execution is using:

```text
local mock simulation
remote MCP server
```

## Next Step

Step 5E can add a Foundry agent adapter interface so the temporary rule-based agent can eventually be replaced cleanly.
