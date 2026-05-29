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
| 5A | Move required entities into tool contracts | `step5/step-5a-required-entities-in-tool-contract.md` |
| 5B | Build validated MCP request payloads from tool contracts and entities | `step5/step-5b-mcp-request-payload-builder.md` |
| 5C | Carry validated request payloads through mock MCP simulation | `step5/step-5c-entity-aware-mock-simulation.md` |
| 5D | Add MCP runtime configuration for mock and future remote execution | `step5/step-5d-mcp-runtime-config.md` |
| 5E | Add Foundry agent adapter boundary | `step5/step-5e-foundry-agent-adapter.md` |
| 5F | Finish Step 5 with readiness checks for MCP config and agent adapter | `step5/step-5f-step-5-readiness-checkpoint.md` |
| 6A | Add MCP executor boundary for mock and future remote execution | `step6/step-6a-mcp-executor-boundary.md` |
| 6B | Add remote MCP request envelope | `step6/step-6b-remote-mcp-request-envelope.md` |
| 6C | Add remote MCP HTTP client placeholder | `step6/step-6c-remote-mcp-http-client-placeholder.md` |
| 6D | Add remote MCP error handling | `step6/step-6d-remote-mcp-error-handling.md` |
| 6E | Add MCP execution diagnostics | `step6/step-6e-mcp-execution-diagnostics.md` |
| 6F | Finish Step 6 with tests and documentation | `step6/step-6f-step-6-completion.md` |
| 7A | Add remote HTTP contract and safe config exposure | `step7/step-7a-remote-http-contract.md` |
| 7B | Implement remote MCP HTTP client | `step7/step-7b-remote-http-client.md` |
| 7C | Add remote auth header support | `step7/step-7c-remote-auth-headers.md` |
| 7D | Normalize remote MCP responses | `step7/step-7d-remote-response-normalization.md` |
| 7E | Add remote MCP error tests | `step7/step-7e-remote-error-tests.md` |
| 7F | Finish Step 7 with docs and verification | `step7/step-7f-step-7-completion.md` |
| Local setup | Create a root Python virtual environment | `local-python-environment.md` |
