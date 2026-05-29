# Step 6A: MCP Executor Boundary

## Goal

Start Step 6 by separating MCP request building from MCP execution.

Step 5 gave us validated MCP request payloads and runtime configuration. Step 6A adds executor classes so the project has a clean place to plug in a real remote Logic Apps Standard MCP transport later.

## What Changed

- Added `McpExecutor` as the stable execution interface.
- Added `MockMcpExecutor` for local sample-response execution.
- Added `RemoteMcpExecutor` as a safe placeholder for future remote MCP calls.
- Added `get_mcp_executor()` to choose the executor from runtime config.
- Updated the MCP client to delegate successful executions to the configured executor.
- Added tests for mock mode, remote mode selection, missing remote endpoint configuration, and not-yet-implemented remote transport.

## Current Behavior

Mock mode remains the default.

When a low-risk ready action runs:

```text
ToolContract + extracted entities
  -> validated McpToolRequest
  -> get_mcp_executor(mock config)
  -> MockMcpExecutor
  -> local sample response
```

Remote mode is intentionally not implemented yet. If selected, it fails clearly instead of pretending that a real enterprise workflow was called.

## Why This Matters

This is the first Step 6 move toward real MCP connectivity. We now have a code-level replacement point for the transport:

- mock executor today
- remote Logic Apps Standard MCP executor later

The agent, risk policy, approval flow, and API response models do not need to change when the transport changes.

## Interview Talking Point

The key architecture choice is separating request construction from execution transport. The project can validate governed MCP payloads locally while still keeping a realistic path to remote enterprise workflow execution.
