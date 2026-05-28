# Enterprise Integration Modernization: Interview Questions

## Project Pitch

**Q: How would you explain this project in one minute?**

This project is an enterprise integration modernization prototype. It shows how an AI agent can safely interact with backend enterprise workflows through approved MCP tools. FastAPI exposes the agent and tool APIs, a controlled tool catalog defines what actions are allowed, risk policy decides whether execution can proceed, and the MCP boundary simulates backend workflow calls. The design keeps Microsoft Foundry first-class for future runtime governance, tracing, evaluations, and operational readiness.

**Q: What business problem does this solve?**

Enterprise users often need to check orders, validate invoices, track shipments, create tickets, or trigger workflows across many systems. This project creates a governed agent pattern where natural-language requests can be mapped to approved integration actions without letting the agent invent tools or bypass policy.

**Q: What makes this an enterprise architecture instead of a simple chatbot?**

The agent does not directly execute arbitrary code. It must select from an approved tool catalog, extract required business entities, pass risk policy, use correlation IDs, and route execution through the MCP boundary. That creates auditability, control, and operational separation.

## Architecture

**Q: What are the main layers?**

1. FastAPI API layer.
2. Agent orchestration layer.
3. Governance and risk policy layer.
4. Approved MCP tool catalog.
5. MCP execution boundary.
6. Backend enterprise systems.
7. Foundry governance, evaluation, and operations layer.

**Q: Why did you separate planning from execution?**

Planning decides what the agent wants to do. Execution actually touches backend workflows. Separating them allows approval gates, validation, audit logging, and human review before business-impacting actions happen.

**Q: Why use MCP as the execution path?**

MCP gives the enterprise a stable boundary for backend actions. Instead of the agent directly calling ERP, ServiceNow, or Logic Apps internals, it calls approved tools with known contracts. That makes tool governance easier.

**Q: Where does FastAPI fit?**

FastAPI is the service interface. It exposes `/agent/chat`, `/tools`, `/tools/{tool_name}/risk`, and `/tools/{tool_name}/simulate`. It maps HTTP requests into internal agent and tool models.

**Q: Where does Microsoft Foundry fit?**

Foundry is planned as the agent runtime and governance layer. In this project, Foundry-specific modules are isolated so runtime, tracing, evaluations, and operational controls can be added without rewriting the API, MCP adapter, or tool policy.

## Agent Behavior

**Q: What happens when a user says `Check order ORD-1001`?**

The agent detects the order intent, selects `getOrderStatus`, extracts `order_id=ORD-1001`, checks that the required entity is present, evaluates risk as `allow`, and returns a planned action. If `simulate_when_ready=true`, it runs mock MCP simulation.

**Q: What happens when a user says `Check order status`?**

The agent selects `getOrderStatus`, but it cannot extract an order ID. The planned action returns `ready_for_simulation=false` and `missing_entities=["order_id"]`.

**Q: What happens for high-risk tools?**

High-risk tools return `risk_decision=require_approval`. If required entities are present and `simulate_when_ready=true`, the chat endpoint stops with `status=approval_required`, does not simulate execution, and returns a pending `approval_request`.

**Q: Why does `/agent/chat` require `simulate_when_ready=true`?**

This keeps execution explicit. By default, chat plans only. Simulation runs only when the caller opts in and the request passes readiness and risk gates.

**Q: Why create an approval request instead of just returning an error?**

A high-risk action is not necessarily invalid. It may be valid but needs human review. Returning a structured approval request preserves the requested tool, entities, reason, correlation ID, and pending status so the workflow can continue safely.

**Q: What happens after an approval request is created?**

A reviewer can call the approval decision API to mark it `approved` or `rejected`. This records the business decision without executing the backend action yet. Execution is intentionally a later governed step.

**Q: How does an approved high-risk action execute?**

The execution endpoint checks that the approval request exists, has a recorded decision, and was approved. Only then does it run the original high-risk MCP simulation through an explicit approved-execution path. The normal direct simulation path still blocks high-risk tools.

**Q: How do you prove what happened later?**

The audit endpoint returns ordered events by correlation ID. It records the plan, approval request, approval decision, and approved execution, which makes the workflow explainable for operations and governance.

**Q: How does this connect to Foundry or Application Insights later?**

The project maps audit events into Foundry-style trace spans and Application Insights-style custom event envelopes. The shared correlation ID becomes the operation ID, so agent planning, approval, and MCP execution can be viewed as one traceable workflow.

**Q: How do you evaluate whether the agent is safe?**

The local evaluation suite checks behavior-focused cases: correct tool selection, missing entity blocking, high-risk approval gating, and unsupported intent clarification. These cases are designed to become Microsoft Foundry evaluation dataset rows later.

**Q: What does operational readiness mean in this project?**

Readiness means the governed execution path is available: approved tool catalog, high-risk risk policy, approval store, audit store, and observability projection. The `/operations/readiness` endpoint summarizes those checks.

## Classes And Contracts

**Q: What is `ToolContract`?**

`ToolContract` is the metadata model for one approved MCP tool. It includes the tool name, business domain, backend system, risk level, owner, version, operational impact, and schema references.

**Q: What is `PlannedAction`?**

`PlannedAction` is the internal object that packages the selected tool, extracted entities, risk decision, approval requirement, readiness, and missing entities before execution.

**Q: What is `RiskDecision`?**

`RiskDecision` is the policy result that says whether the selected tool is allowed to run or requires human approval.

**Q: What is `McpSimulationResult`?**

`McpSimulationResult` is the result returned by the mock MCP execution boundary. It includes tool name, correlation ID, mode, status, risk decision, approval requirement, result payload, and message.

## Governance And Safety

**Q: How do you prevent the agent from inventing tools?**

Tool selection is constrained to the static approved registry. If a selected tool is not in the catalog, the request is treated as unsupported.

**Q: How do you handle auditability?**

Every response can carry a correlation ID. Risk decisions include audit requirements, and tool metadata includes owner, backend system, risk level, and operational impact.

**Q: Why are some tools high risk?**

High-risk tools can create external or operational business impact, such as sending supplier notifications or creating ServiceNow tickets. Those require approval before execution.

**Q: Why are read-only tools still governed?**

Read-only actions can still expose sensitive operational or business data. They may be allowed automatically, but they should still be auditable.

## Testing

**Q: What did you test?**

The tests cover health checks, tool catalog APIs, risk APIs, mock simulation, correlation IDs, chat intent detection, entity extraction, planned actions, missing required entities, and gated chat-triggered simulation.

**Q: What is a strong test case from this project?**

One strong test verifies that a high-risk tool with required entities still does not simulate from chat. That proves readiness alone is not enough; policy must also allow execution.

**Q: What did the latest verification show?**

The latest test run passed 36 tests. The only warnings were pytest cache write warnings due local `.pytest_cache` access.

## Design Choices

**Q: Why start with mock simulation instead of real Azure calls?**

Mock simulation lets us prove the architecture, contracts, risk gates, and tests before connecting to real enterprise systems. It lowers risk while preserving the target design.

**Q: Why keep Foundry code isolated?**

SDKs and runtime details can evolve. Isolating Foundry-specific code protects the core API, MCP adapter, and governance model from churn.

**Q: Why use explicit schemas?**

Explicit request and response schemas make the API predictable for future front ends, tests, integrations, and documentation.

## Resume Answers

**Q: How would you describe this project on a resume?**

Built an enterprise integration modernization prototype using FastAPI, governed MCP tool contracts, risk-based execution policy, correlation-aware mock execution, and an agent planning layer designed for Microsoft Foundry governance, evaluations, and operations.

**Q: What technical skills does this demonstrate?**

FastAPI, Python, API design, agent orchestration, MCP tool governance, enterprise integration patterns, risk-based execution control, test-driven development, and Azure-aligned architecture.

**Q: What architecture skills does this demonstrate?**

Separation of concerns, contract-first tool design, policy-driven execution, auditability, controlled backend access, and phased modernization from mock simulation toward real cloud integrations.

## Possible Follow-Up Improvements

**Q: What would you build next?**

1. Add an approval request flow for high-risk actions.
2. Add real MCP server integration backed by Logic Apps Standard.
3. Add Foundry tracing and evaluation datasets.
4. Add a front end for chat, tool catalog, risk decisions, and simulation results.
5. Add role-based access control for who can run or approve tools.
6. Add persistent audit logs for planned actions and executions.

**Q: What production concerns remain?**

Authentication, authorization, secret management, real MCP connectivity, telemetry export, approval workflow persistence, rate limiting, input validation hardening, and deployment pipelines.
