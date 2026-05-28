# Step 2B: Risk Policy

## What We Built

We added the first execution policy for MCP tools.

The tool catalog says what tools exist. The risk policy says whether a selected tool can execute immediately or must stop for approval.

## Policy Rules

| Risk Level | Decision | Why |
|---|---|---|
| Low | Allow | Read-only lookups can run with audit logging. |
| Medium | Allow | Validation and approval-task creation can run with audit logging. |
| High | Require approval | External communication or ticket creation can create business impact. |

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/tools/risk_policy.py` | Implements the execution decision logic. |
| `agent/tests/test_risk_policy.py` | Proves low, medium, high, and unknown tool behavior. |
| `development/README.md` | Adds this step to the learning index. |

## Key Learning

This is where the project starts to feel enterprise-ready.

An AI agent should not simply call any workflow it understands. It must pass through policy first:

1. Is this an approved tool?
2. What is the risk level?
3. Does this action require approval?
4. Should we audit the decision?

## Example

`getOrderStatus` is low risk because it is read-only.

`sendSupplierNotification` is high risk because it sends an external message. The agent must request approval before execution.

## Next Step

Step 2C will connect the catalog and risk policy to the FastAPI `/tools` endpoints so we can view the approved tool list through the API.
