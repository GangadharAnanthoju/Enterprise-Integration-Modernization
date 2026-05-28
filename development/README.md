# Development Learning Notes

This folder captures the project build in small learning steps.

The goal is to make the AI project understandable from an Azure Integration Services point of view:

- Logic Apps workflows become MCP tools.
- The tool registry works like an enterprise API/tool catalog.
- Risk policy controls whether an agent can execute a tool directly or must request approval.
- Microsoft Agent Framework orchestrates the agent.
- Microsoft Foundry governs runtime, tracing, evaluations, and release readiness.

## Step Index

| Step | Topic | File |
|---|---|---|
| 2A | Define approved MCP tool catalog in code | `step2/step-2a-tool-catalog.md` |
| 2B | Add risk policy for tool execution decisions | `step2/step-2b-risk-policy.md` |
| 2C | Expose the approved tool catalog through FastAPI | `step2/step-2c-tool-catalog-api.md` |
| 2D | Expose risk decisions through FastAPI | `step2/step-2d-risk-decision-api.md` |
| 2E | Simulate approved MCP tools with local sample responses | `step2/step-2e-mock-tool-simulation.md` |
| 2F | Add correlation IDs to mock tool simulations | `step2/step-2f-correlation-ids.md` |
| 2G | Add a safe agent chat placeholder | `step2/step-2g-agent-chat-placeholder.md` |
| 3A | Add simple intent detection to the agent chat shell | `step3/step-3a-simple-intent-detection.md` |
| 3B | Extract business identifiers from chat messages | `step3/step-3b-business-entity-extraction.md` |
| 3C | Return a structured planned action from chat | `step3/step-3c-planned-action-object.md` |
| 3D | Check required entities before simulation readiness | `step3/step-3d-required-entities.md` |
| 3E | Gate optional chat-triggered mock simulation | `step3/step-3e-chat-simulation-gate.md` |
| 3F | Create approval requests for ready high-risk actions | `step3/step-3f-approval-request-flow.md` |
| 3G | Approve or reject pending approval requests | `step3/step-3g-approval-decision.md` |
| 3H | Execute approved high-risk actions through MCP simulation | `step3/step-3h-execute-approved-action.md` |
| 4A | Record audit events for governed agent workflows | `step4/step-4a-audit-events.md` |
| 4B | Project audit events into Foundry and App Insights observability shapes | `step4/step-4b-foundry-observability.md` |
| 4C | Add local Foundry-style evaluation suite | `step4/step-4c-local-evaluation-suite.md` |
| 4D | Add operational readiness checks | `step4/step-4d-operational-readiness.md` |
| Local setup | Create a root Python virtual environment | `local-python-environment.md` |
