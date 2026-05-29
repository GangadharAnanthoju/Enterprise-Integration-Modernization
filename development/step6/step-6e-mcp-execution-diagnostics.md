# Step 6E: MCP Execution Diagnostics

## Goal

Expose safe diagnostics for the active MCP executor and enrich audit details with execution payload context.

## What Changed

- Added `/mcp/executor`.
- Added `McpExecutorDiagnosticsResponse`.
- Added executor diagnostics for mock and remote modes.
- Added MCP request payload details to tool execution audit events.

## Why This Matters

Operators should be able to answer:

- Are we using mock execution or remote execution?
- Which executor class is active?
- Is the remote endpoint configured?
- What validated payload reached the MCP execution boundary?

## Interview Talking Point

This step treats execution mode as an operations concern. The API can safely expose runtime diagnostics without leaking secrets or backend credentials.
