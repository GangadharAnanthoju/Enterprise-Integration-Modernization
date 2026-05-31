# Step 15C - Step 15 Completion

## Goal

Close Step 15 by confirming the Foundry evaluation foundation is ready for the next phase.

## Completed In Step 15

Step 15 created the bridge from local regression tests to Foundry-ready evaluation assets.

Completed:

- planned the Foundry evaluation strategy
- defined evaluation layers:
  - plan contract
  - governed outcome
  - safety regression
  - future end-to-end MCP integration
- exported local evaluation cases into JSONL
- committed a reviewable dataset artifact
- added tests for the exporter
- updated roadmap and interview notes

## Current Dataset

The current dataset is:

```text
foundry/evaluations/datasets/enterprise-mcp-regression.jsonl
```

It contains these cases:

| Case | Purpose |
|---|---|
| `eval-order-ready` | Low-risk ready execution |
| `eval-order-missing-id` | Missing required entity handling |
| `eval-supplier-approval` | High-risk approval gating |
| `eval-unknown-intent` | Unsupported request clarification |

## What Step 15 Does Not Do Yet

Step 15 does not run a live Foundry evaluation job yet.

That should come later after we decide the exact Foundry evaluation API path and whether the target is:

- plan-only evaluation
- FastAPI governed outcome evaluation
- end-to-end MCP/Logic Apps evaluation

## Next Recommended Step

Move to Step 16 when ready:

```text
Azure Logic Apps deployment planning
```

The low-cost path is still to keep Logic Apps local until you approve the Azure resource plan.
