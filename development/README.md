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
| 8A | Plan Azure environment configuration for remote MCP and Foundry | `step8/step-8a-azure-environment-plan.md` |
| 8B | Add safe `.env.example` for mock and remote modes | `step8/step-8b-env-example.md` |
| 8C | Add environment validation checks | `step8/step-8c-environment-validation.md` |
| 8D | Connect environment validation to readiness checks | `step8/step-8d-remote-readiness-checks.md` |
| 8E | Document Foundry and observability environment settings | `step8/step-8e-foundry-observability-env-notes.md` |
| 8F | Finish Step 8 environment foundation | `step8/step-8f-step-8-completion.md` |
| 9A | Start Logic Apps MCP workflow implementation | `step9/step-9a-logic-apps-mcp-plan.md` |
| 9B | Define getOrderStatus Logic Apps MCP contract | `step9/step-9b-get-order-status-contract.md` |
| 9C | Configure local getOrderStatus Logic Apps workflow design | `step9/step-9c-local-logic-app-workflow-design.md` |
| 9D | Add Logic Apps Standard project structure for designer work | `step9/step-9d-logic-apps-standard-project.md` |
| 9E | Add Logic Apps designer workspace and local setup notes | `step9/step-9e-logic-apps-designer-workspace.md` |
| 9F | Configure Logic Apps local resource group setting | `step9/step-9f-logic-apps-local-resource-group.md` |
| 9G | Add local Logic App run instructions | `step9/step-9g-local-logic-app-run-instructions.md` |
| 9H | Complete local Logic Apps workflow set | `step9/step-9h-complete-local-workflow-set.md` |
| 10A | Review Azure resources before Logic Apps deployment | `step10/step-10a-azure-resource-review.md` |
| 10B | Connect remote MCP mode to local Logic Apps | `step10/step-10b-local-logic-apps-remote-mcp.md` |
| 10C | Add per-tool Logic Apps endpoint mapping | `step10/step-10c-per-tool-logic-app-endpoints.md` |
| 10D | Add checkShipmentStatus local MCP workflow | `step10/step-10d-check-shipment-status-local-mcp.md` |
| 10E | Add validateInvoice local MCP workflow | `step10/step-10e-validate-invoice-local-mcp.md` |
| 10F | Add queryIntegrationRunStatus local MCP workflow | `step10/step-10f-query-integration-run-status-local-mcp.md` |
| 10G | Add high-risk local MCP workflows | `step10/step-10g-high-risk-local-mcp-workflows.md` |
| 10H | Complete local MCP workflow set | `step10/step-10h-complete-local-mcp-workflow-set.md` |
| 11A | Plan the Foundry agent architecture | `step11/step-11a-foundry-agent-architecture-plan.md` |
| 11B | Create Foundry agent instructions | `step11/step-11b-foundry-agent-instructions.md` |
| 11C | Add Foundry agent configuration skeleton | `step11/step-11c-foundry-agent-config.md` |
| 11D | Add Foundry tool registration metadata | `step11/step-11d-foundry-tool-registration-metadata.md` |
| 11E | Connect Foundry artifacts to readiness checks | `step11/step-11e-foundry-readiness-integration.md` |
| 11F | Finish Step 11 Foundry preparation | `step11/step-11f-step-11-completion.md` |
| 12A | Plan real Foundry resources and agent creation path | `step12/step-12a-foundry-resource-plan.md` |
| 12B | Capture Foundry environment checklist | `step12/step-12b-foundry-environment-checklist.md` |
| 12C | Plan MAF-backed Foundry agent registration | `step12/step-12c-maf-foundry-registration-plan.md` |
| 12D | Add local MAF agent skeleton | `step12/step-12d-local-maf-agent-skeleton.md` |
| 12E | Plan Foundry invocation boundary | `step12/step-12e-foundry-invocation-boundary-plan.md` |
| 12F | Finish Step 12 MAF and Foundry preparation | `step12/step-12f-step-12-completion.md` |
| Azure setup | Environment variable guide for local and Azure settings | `azure-environment-setup.md` |
| Local setup | Create a root Python virtual environment | `local-python-environment.md` |
