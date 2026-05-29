# Step 8B: Environment Example File

## Goal

Add a safe `.env.example` template for local mock mode and future remote MCP mode.

Step 8A planned the environment strategy. Step 8B turns that plan into a concrete file developers can copy when setting up the project.

## What Changed

- Updated `agent/.env.example`.
- Made mock MCP mode the safe default.
- Added explicit MCP runtime fields:
  - `MOCK_MCP`
  - `MCP_EXECUTION_MODE`
  - `MCP_SERVER_NAME`
  - `MCP_SERVER_URL`
  - `MCP_API_KEY`
  - `MCP_TIMEOUT_SECONDS`
- Added Foundry placeholders.
- Added observability placeholders.
- Added Azure identity and Key Vault placeholders.

## How To Use It

Copy the example file to a private `.env`:

```powershell
Copy-Item agent\.env.example agent\.env
```

Keep `agent\.env` private. It is ignored by git.

## Local Mock Mode

This is the default:

```env
MOCK_MCP=true
MCP_EXECUTION_MODE=mock
```

## Remote MCP Mode

Use this only when a real endpoint exists:

```env
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_SERVER_URL=https://your-logic-app-or-mcp-endpoint
MCP_API_KEY=your-secret-value
```

## Why This Matters

The project now has a tested remote MCP HTTP client. The `.env.example` makes it clear how to keep local work safe while leaving a deliberate path to remote Azure execution.

## Interview Talking Point

I kept the repository safe by committing only a template. Developers copy it into a private `.env`, and production deployments should use Key Vault or platform configuration for secrets.
