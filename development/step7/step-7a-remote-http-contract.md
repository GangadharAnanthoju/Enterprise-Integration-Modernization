# Step 7A: Remote HTTP Contract

## Goal

Make the remote MCP transport contract concrete enough for real HTTP execution.

Step 6 introduced the envelope. Step 7A keeps that envelope as the HTTP JSON body and adds safe configuration metadata such as whether an API key is configured without exposing the secret.

## What Changed

- `McpServerConfig` now tracks `api_key`.
- The API exposes `api_key_configured`, not the API key value.
- Tests verify mock and remote config do not leak secrets.

## Interview Talking Point

The project separates secret presence from secret value. Operators can see whether authentication is configured without exposing credentials.
