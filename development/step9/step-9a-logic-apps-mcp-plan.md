# Step 9A: Logic Apps MCP Implementation Plan

## Goal

Start the real Azure integration phase: create Logic Apps workflows and expose them as MCP tools.

This is the step where the project moves from a tested remote client path to real Azure-backed integration workflows.

## Starting Tool

Begin with one low-risk read-only tool:

```text
getOrderStatus
```

Why this one first:

- it is low risk
- it needs one clear entity: `order_id`
- it already has a tool contract
- it already has tests and mock sample data
- it is easy to compare mock output and remote output

## Step 9 Roadmap

| Step | Purpose |
|---|---|
| 9A | Plan Logic Apps MCP workflow implementation |
| 9B | Define the `getOrderStatus` Logic Apps workflow contract |
| 9C | Create or document the Logic Apps workflow trigger and response |
| 9D | Configure `MCP_SERVER_URL` and `MCP_API_KEY` for remote mode |
| 9E | Run remote-mode smoke test for `getOrderStatus` |
| 9F | Add docs showing how Logic Apps maps to MCP tools |

## Target Flow

```text
/agent/chat
  -> ToolContract(getOrderStatus)
  -> required entity validation
  -> risk policy allow
  -> McpToolRequest
  -> RemoteMcpHttpClient
  -> Logic Apps Standard MCP endpoint
  -> order status response
```

## Interview Talking Point

I did not start with Azure workflows first. I first built governance, validation, and remote execution safety. Then I connected Logic Apps as the backend implementation of approved MCP tools.
