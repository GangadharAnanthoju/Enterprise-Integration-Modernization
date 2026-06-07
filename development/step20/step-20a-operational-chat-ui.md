# Step 20A - Operational Chat UI

## Goal

Make the governed enterprise integration agent usable without manually calling
FastAPI endpoints.

## Implementation

The UI is a no-build static frontend served by the existing FastAPI Container
App at:

```text
/ui/
```

It provides:

- governed chat planning and execution
- execute-when-policy-allows control
- selected tool, entities, risk decision, and correlation ID
- high-risk approval and rejection decisions
- approved high-risk action execution
- audit timeline
- FastAPI, Foundry adapter, MCP, and readiness posture
- Montserrat typography and a compact three-column operations layout
- quick-action prompts and a visible risk-policy legend

Visual direction is aligned with the existing Sysint loan pre-screening portal:
deep navy operations surfaces, compact command-bar styling, and teal/cyan
status accents.

The UI uses relative same-origin API calls, so it can run locally or behind a
future gateway path without embedding backend URLs or credentials.

## Architecture Decision

No frontend framework or separate hosting service was added yet. This keeps the
learning project focused:

```text
browser -> FastAPI static UI -> FastAPI governance API -> Foundry -> MCP -> Logic Apps
```

A separate frontend can be introduced later if authentication, independent
release cadence, or a richer component system requires it.

## Validation

```text
UI asset and redirect tests: passed
JavaScript syntax check: passed
Low-risk chat execution through local UI backend: passed
High-risk approval, decision, execution, and audit flow: passed
Full offline suite: 158 passed
```
