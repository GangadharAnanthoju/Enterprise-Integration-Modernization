# Step 7C: Remote Auth Headers

## Goal

Add authentication header support for the future Logic Apps Standard MCP endpoint.

## What Changed

- If `mcp_api_key` is configured, the remote client sends `Authorization: Bearer <token>`.
- The public config endpoint only returns `api_key_configured`.
- Tests verify the header is sent in mocked remote calls.

## Why This Matters

Enterprise execution endpoints must be authenticated, but secrets should not appear in diagnostics, audit payloads, or API responses.

## Interview Talking Point

This step shows secure operational design: expose whether auth is configured, never expose the secret itself.
