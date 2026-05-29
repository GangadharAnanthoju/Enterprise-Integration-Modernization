# Step 7B: Remote HTTP Client

## Goal

Implement the remote MCP HTTP client using `httpx`.

## What Changed

- `RemoteMcpHttpClient.send()` now performs an HTTP POST.
- It sends the remote MCP envelope as JSON.
- It includes correlation and tool-name headers.
- It adds a bearer authorization header when an MCP API key is configured.
- Tests use `httpx.MockTransport` so no live network endpoint is required.

## Interview Talking Point

The HTTP client is real, but tests are isolated from the network. That keeps the implementation production-shaped without making local development depend on Azure connectivity.
