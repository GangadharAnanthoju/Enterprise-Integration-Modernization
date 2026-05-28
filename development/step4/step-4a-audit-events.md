# Step 4A: Audit Events

## What We Built

We added audit events for the governed agent workflow.

The project now records local audit events when:

1. `/agent/chat` creates a plan.
2. A high-risk approval request is created.
3. A reviewer approves or rejects the request.
4. An approved high-risk action executes through MCP simulation.

## Endpoint

```text
GET /audit/{correlation_id}
```

Example:

```text
GET /audit/chat-corr-009
```

Response includes an ordered list:

```json
[
  {
    "event_type": "agent_chat_planned",
    "source": "agent.chat",
    "status": "approval_required"
  },
  {
    "event_type": "approval_request_created",
    "source": "agent.chat",
    "status": "pending"
  },
  {
    "event_type": "approval_decision_recorded",
    "source": "approvals.decision",
    "status": "approved"
  },
  {
    "event_type": "approved_action_executed",
    "source": "approvals.execute",
    "status": "completed"
  }
]
```

## Why This Matters

Enterprise AI workflows need traceability.

It should be possible to explain:

```text
What did the agent plan?
Why was approval required?
Who approved or rejected it?
Was the action executed?
Which correlation ID ties the workflow together?
```

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/audit/events.py` | Adds temporary in-memory audit event store. |
| `agent/src/audit/__init__.py` | Marks audit helpers as a package. |
| `agent/src/api/schemas.py` | Adds `AuditEventResponse`. |
| `agent/src/api/routes.py` | Records audit events and exposes `/audit/{correlation_id}`. |
| `agent/tests/test_agent_flow.py` | Tests workflow audit timeline and unknown correlation lookup. |

## Key Learning

Audit is not just logging errors.

For governed AI, audit captures decisions and state transitions: planning, approval request, human decision, and execution.

## Next Step

Step 4B can connect audit and traces to Microsoft Foundry or Azure Monitor concepts.
