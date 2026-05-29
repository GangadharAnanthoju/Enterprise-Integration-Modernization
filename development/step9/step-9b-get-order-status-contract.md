# Step 9B: getOrderStatus Logic Apps MCP Contract

## Goal

Define the first real Logic Apps MCP workflow contract before creating or deploying the workflow.

We start with `getOrderStatus` because it is low risk and read-only. This lets us prove the end-to-end remote MCP shape without triggering a business-changing action.

## What Changed

- Updated `logicapps/workflows/getOrderStatus/README.md`.
- Updated `sample-request.json` to match the governed MCP payload.
- Added `logicapps/workflows/getOrderStatus/contract.json`.
- Added tests that compare the Logic Apps contract to the Python `ToolContract`.

## Contract Summary

| Field | Value |
|---|---|
| Tool | `getOrderStatus` |
| Workflow | `getOrderStatus` |
| Method | `POST` |
| Risk | Low |
| Approval required | No |
| Required entity | `order_id` |

## Request Payload

The governed MCP request payload is:

```json
{
  "order_id": "ORD-1001"
}
```

## Backend Mapping

The workflow can map the governed MCP field to whatever the backend order service expects:

```text
MCP payload: order_id
Backend lookup field: orderNumber
```

## Response Payload

The sample response remains:

```json
{
  "orderNumber": "4500098123",
  "status": "In Transit",
  "estimatedDeliveryDate": "2026-05-21",
  "delayRisk": "Medium",
  "correlationId": "abc-123"
}
```

## Why This Matters

This is the first direct bridge between our approved MCP tool catalog and a planned Logic Apps workflow. The test ensures the Logic Apps contract does not drift away from the agent's governed `ToolContract`.

## Interview Talking Point

I started Logic Apps MCP implementation with a low-risk read-only workflow. Before deploying anything, I defined the request, response, risk, required entities, and backend mapping so the workflow matches the governed MCP tool contract.
