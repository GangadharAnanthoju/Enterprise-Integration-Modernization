# Step 6D: Remote MCP Error Handling

## Goal

Define explicit remote MCP failure types before real network calls are added.

## What Changed

- Added `RemoteMcpConfigurationError`.
- Added `RemoteMcpNotImplementedError`.
- Added `RemoteMcpTimeoutError`.
- Added `RemoteMcpAuthenticationError`.
- Added `RemoteMcpBackendError`.
- Added `map_remote_http_error()` to convert HTTP-style failures into MCP exceptions.

## Why This Matters

Enterprise integrations fail in different ways. A timeout is different from an authentication failure, and both are different from a backend workflow failure. Clear exception types make diagnostics, retries, alerts, and audit trails easier.

## Interview Talking Point

Instead of treating all remote failures as generic exceptions, I modeled failure modes that matter operationally: config, auth, timeout, and backend failure.
