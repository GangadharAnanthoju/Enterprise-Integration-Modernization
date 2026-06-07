# Demo Script

This demo shows a Foundry-governed agent using MCP tools to modernize enterprise integration workflows.

## Opening Narrative

This is not a general chatbot. It is a governed enterprise integration assistant. Microsoft Agent Framework handles orchestration, Microsoft Foundry provides runtime governance and evaluations, and Azure Logic Apps exposes approved workflows as MCP tools.

## Scenario 1: Read-Only Order Lookup

Prompt:

```text
What is the status of order ORD-1001?
```

Expected behavior:

- Agent selects `getOrderStatus`.
- Risk policy marks it low risk.
- Managed Logic Apps MCP workflow returns order status.
- Response includes the order status and correlation ID.

## Scenario 2: Invoice Validation

Prompt:

```text
Validate invoice INV-2001 before payment processing.
```

Expected behavior:

- Agent selects `validateInvoice`.
- Risk policy marks it medium risk.
- Validation result explains pass/fail rules.
- No backend payment action is performed.

## Scenario 3: High-Risk Supplier Notification

Prompt:

```text
Notify the supplier that shipment SHIP-3001 is delayed.
```

Expected behavior:

- Agent selects `sendSupplierNotification`.
- Risk policy marks it high risk.
- Agent creates or requests approval before sending.
- Response makes clear that notification is pending approval.

## Scenario 4: Operations Troubleshooting

Prompt:

```text
Check integration run status for correlation ID demo-corr-001.
```

Expected behavior:

- Agent selects `queryIntegrationRunStatus`.
- Response summarizes the run status, failed step if any, and next action.
- Monitoring view can find the same correlation ID.

## Close

Show the approval audit trail, managed MCP tool catalog, Application Insights
telemetry, and GitHub release evidence to connect the demo behavior to
production-style controls.
