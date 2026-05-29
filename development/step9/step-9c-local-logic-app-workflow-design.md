# Step 9C: Local Logic Apps Workflow Design

## Goal

Turn the `getOrderStatus` local workflow placeholder into an inspectable Logic Apps workflow definition.

This does not deploy to Azure yet. It gives us a real local `workflow.json` shape that can be opened and reviewed like a Logic Apps workflow design.

## What Changed

- Filled in `logicapps/workflows/getOrderStatus/workflow.json`.
- Added an HTTP request trigger.
- Added a request schema requiring `order_id`.
- Added a validation condition.
- Added a success response.
- Added a missing-`order_id` bad-request response.
- Added tests that verify the workflow has the expected local design pieces.

## Workflow Shape

```text
HTTP Request Trigger
  -> Validate_order_id
      -> true:
          Compose_order_status_response
          Return_order_status 200
      -> false:
          Return_missing_order_id 400
```

## Why This Matters

Before connecting to Azure, we can inspect and test the intended Logic Apps workflow shape locally. This makes the workflow contract visible and keeps the implementation aligned with the MCP tool catalog.

## Interview Talking Point

I configured the first Logic Apps workflow locally as an HTTP-triggered stateful workflow. It validates the governed MCP payload and returns a predictable JSON response, which is the first concrete step toward exposing Logic Apps as MCP tools.
