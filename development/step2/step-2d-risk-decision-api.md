# Step 2D: Risk Decision API

## What We Built

We exposed the pre-execution risk policy through FastAPI.

This lets a caller ask:

```text
Can this approved MCP tool execute now, or does it require approval?
```

## New API Endpoint

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/tools/{tool_name}/risk` | Returns the risk decision for one approved MCP tool. |

## Example URLs

```text
http://127.0.0.1:8000/tools/getOrderStatus/risk
http://127.0.0.1:8000/tools/sendSupplierNotification/risk
```

## Example Low-Risk Response

```json
{
  "tool_name": "getOrderStatus",
  "risk_level": "low",
  "decision": "allow",
  "approval_required": false,
  "audit_required": true,
  "reason": "Low-risk read-only tools can execute with standard audit logging."
}
```

## Example High-Risk Response

```json
{
  "tool_name": "sendSupplierNotification",
  "risk_level": "high",
  "decision": "require_approval",
  "approval_required": true,
  "audit_required": true,
  "reason": "High-risk enterprise actions require human approval before execution."
}
```

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/api/schemas.py` | Adds the risk decision API response shape. |
| `agent/src/api/routes.py` | Adds `/tools/{tool_name}/risk`. |
| `agent/tests/test_agent_flow.py` | Adds API tests for low-risk, high-risk, and unknown tool risk decisions. |
| `development/README.md` | Adds this step to the learning index. |

## Key Learning

This is the first visible governance check in the API.

The agent should eventually follow this same flow:

1. Select a tool from the approved catalog.
2. Ask risk policy for a decision.
3. Execute only if allowed.
4. Pause for approval if required.

## Next Step

Step 2E can add a mock simulation endpoint:

```text
POST /tools/{tool_name}/simulate
```

That will let us test read-only workflow behavior without connecting to Azure yet.
