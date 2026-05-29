# Step 6B: Remote MCP Request Envelope

## Goal

Define the request shape that will eventually be sent to a remote Logic Apps Standard MCP server.

Step 5 built `McpToolRequest` from validated tool metadata and extracted entities. Step 6B wraps that request in a transport envelope with server name, endpoint URL, correlation ID, payload, and timeout.

## What Changed

- Added `McpRemoteRequestEnvelope`.
- Added `build_remote_request_envelope()`.
- Added `to_http_json()` so the future transport has a clear JSON body.

## Why This Matters

The agent should not send arbitrary JSON to a backend workflow. The payload must come from the governed MCP request builder first, then be wrapped for transport.

## Flow

```text
ToolContract + entities
  -> McpToolRequest
  -> McpRemoteRequestEnvelope
  -> future HTTP transport
```

## Interview Talking Point

This step separates business payload validation from transport concerns. That makes the request auditable before it ever reaches a remote system.
