# Step 7D: Remote Response Normalization

## Goal

Normalize remote MCP HTTP responses into the same execution output shape used by mock execution.

## What Changed

- The remote client parses JSON responses.
- `RemoteMcpExecutor` returns `McpExecutionOutput`.
- The rest of the agent/API path can keep using the same response mapping.

## Why This Matters

Mock and remote execution should differ in transport, not in how the rest of the system handles the result.

## Interview Talking Point

The remote executor normalizes backend responses so the API, audit, and Foundry projections do not need transport-specific branches.
