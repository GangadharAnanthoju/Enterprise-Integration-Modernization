# Step 4B: Foundry Observability Projection

## What We Built

We connected local audit events to Foundry-style traces and Application Insights-style custom event envelopes.

This step does not call Azure yet. It creates the shape we would later send to Microsoft Foundry, Azure Monitor, or Application Insights.

## New Endpoints

```text
GET /foundry/traces/{correlation_id}
GET /observability/appinsights/{correlation_id}
```

## Why This Matters

Step 4A recorded audit events.

Step 4B turns those audit events into observability records:

```text
Audit event
  -> Foundry trace span
  -> Application Insights custom event
```

This lets us explain both business governance and operational telemetry from the same correlation ID.

## Audit To Foundry Trace Mapping

| Audit Event | Foundry Span Name | Span Kind |
|---|---|---|
| `agent_chat_planned` | `agent_chat_planned` | `agent` |
| `approval_request_created` | `approval_request_created` | `approval` |
| `approval_decision_recorded` | `approval_decision_recorded` | `approval` |
| `approved_action_executed` | `approved_action_executed` | `tool` |
| `tool_simulation_completed` | `tool_simulation_completed` | `tool` |

## Example Foundry Trace Response

```json
[
  {
    "trace_id": "audit-0001",
    "correlation_id": "chat-corr-010",
    "span_name": "agent_chat_planned",
    "span_kind": "agent",
    "status": "approval_required",
    "source": "agent.chat",
    "attributes": {
      "selected_tool": "sendSupplierNotification",
      "risk_decision": "require_approval"
    }
  }
]
```

## Application Insights Projection

Each Foundry-style trace becomes an Application Insights custom event envelope:

```json
{
  "name": "enterprise.integration.agent_chat_planned",
  "operation_id": "chat-corr-011",
  "severity": "warning",
  "properties": {
    "trace_id": "audit-0001",
    "span_kind": "agent",
    "source": "agent.chat",
    "status": "approval_required"
  }
}
```

`operation_id` is the correlation ID. That is the value operators would use to connect all events in one workflow.

## Severity Rule

| Status | Severity |
|---|---|
| `approval_required` | `warning` |
| `rejected` | `warning` |
| Anything else | `information` |

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/foundry/tracing.py` | Adds Foundry-style trace records and audit-to-trace mapping. |
| `agent/src/telemetry/appinsights.py` | Adds Application Insights custom event projection. |
| `agent/src/api/schemas.py` | Adds trace and App Insights response schemas. |
| `agent/src/api/routes.py` | Adds observability endpoints. |
| `agent/tests/test_agent_flow.py` | Tests trace and App Insights projections. |

## Key Learning

Audit and observability are related but not identical.

Audit explains business decisions:

```text
Who approved this?
Why did execution happen?
What tool was requested?
```

Observability explains runtime behavior:

```text
Which spans happened?
Which operation ID connects them?
Which stage failed or required attention?
```

## Future Azure Integration

Later, these local records can map to:

| Local Concept | Azure / Foundry Concept |
|---|---|
| `correlation_id` | Application Insights `operation_Id` |
| `FoundryTraceRecord` | Foundry trace span or OpenTelemetry span |
| `AppInsightsCustomEvent` | Application Insights `customEvents` |
| `span_kind=agent` | Agent planning span |
| `span_kind=tool` | MCP/tool execution dependency span |
| `span_kind=approval` | Human workflow/business process span |

## Next Step

Step 4C can add evaluation datasets for safe tool selection and approval behavior.
