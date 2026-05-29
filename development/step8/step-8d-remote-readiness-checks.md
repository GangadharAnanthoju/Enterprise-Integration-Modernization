# Step 8D: Remote Readiness Checks

## Goal

Connect environment validation to operational readiness.

Step 8C answers whether settings are valid. Step 8D makes `/operations/readiness` include that answer so operators can see whether the system is safe for the selected mode.

## What Changed

- Added an `environment_validation` readiness check.
- Updated readiness tests.
- Remote mode with missing `MCP_SERVER_URL` or `MCP_API_KEY` now makes readiness return `needs_attention`.

## Why This Matters

Readiness should reflect the mode the app is trying to run in:

- Mock mode can be ready without real Azure settings.
- Remote MCP mode cannot be ready without endpoint and auth settings.

## Interview Talking Point

I separated environment validation from readiness, then connected them. That lets developers inspect detailed configuration checks while readiness gives operations one deployment-friendly status.
