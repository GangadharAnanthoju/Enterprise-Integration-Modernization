# Enterprise Integration Modernization: Interview Questions

## Project Overview

**Q: How would you explain this project in one minute?**

I built an enterprise integration modernization prototype where an AI agent can safely interact with backend workflows through approved MCP tools. The agent does not call systems directly. It selects a governed tool, validates required business entities, applies risk policy, uses approval gates for high-risk actions, and executes through Logic Apps workflows using a consistent MCP envelope. The design is aligned to Microsoft Foundry for future agent runtime, evaluations, tracing, and operations.

**Q: What problem does this solve?**

Enterprise users often need to check orders, validate invoices, track shipments, troubleshoot integration runs, or trigger operational workflows across multiple systems. This project creates a controlled pattern where natural-language requests can become approved integration actions without letting the agent invent tools or bypass enterprise policy.

**Q: What makes this more than a chatbot?**

The agent is not just generating text. It is part of a governed integration flow. It uses an approved tool catalog, required-entity validation, risk decisions, approval workflows, audit events, correlation IDs, and a dedicated MCP execution boundary before any backend action can happen.

**Q: How would you describe the architecture at a high level?**

The main layers are FastAPI, agent orchestration, tool governance, risk policy, approval handling, MCP execution, Logic Apps workflows, and Foundry-oriented operations. FastAPI exposes the API, the agent plans the action, the registry controls available tools, risk policy decides whether approval is needed, and Logic Apps executes the enterprise workflow through MCP-style HTTP envelopes.

## Agent Architecture

**Q: What is the agent responsible for?**

The agent is responsible for understanding the user's request, selecting an approved tool, extracting required business entities, asking for missing information, and explaining the planned action. It should not directly execute backend logic or bypass policy.

**Q: How do you prevent the agent from inventing tools?**

Tool selection is constrained to a static approved registry. If the request does not match an approved tool, the agent returns a clarification response instead of creating a new tool name or making an arbitrary backend call.

**Q: Why did you separate planning from execution?**

Planning decides what the agent wants to do. Execution touches backend workflows. Separating them allows validation, risk checks, approval gates, audit logging, and operational controls before any business-impacting action happens.

**Q: How would you replace the current local rule-based agent with a real Foundry agent?**

FastAPI already calls an agent adapter instead of directly depending on the local planner. The local adapter can later be replaced with a Foundry agent adapter that returns the same structured plan: selected tool, extracted entities, missing entities, and risk-aware execution decision. That keeps the public API stable while changing the runtime.

**Q: What instructions would you give the Foundry agent?**

I would instruct it to use only approved tools, never invent tool names, ask for missing entities, preserve correlation IDs, explain its reasoning briefly, and never execute high-risk tools without approval. It should treat MCP as the only enterprise execution path.

**Q: Why write agent instructions before creating the Foundry agent?**

The instructions are the behavior contract for the agent. They define tool limits, missing-entity behavior, approval rules, response style, and MCP execution boundaries. Once those are clear, creating the Foundry agent and attaching tools becomes much less ambiguous.

**Q: What is the purpose of the Foundry agent configuration skeleton?**

It captures the intended Foundry agent metadata before live registration: agent name, instruction file, current local adapter, MCP execution boundary, Logic Apps backend, approved tool placeholders, governance source files, and evaluation expectations. It is not a deployed Foundry resource yet; it is the bridge between the local implementation and future Foundry registration.

**Q: How would you prepare tool registration for Foundry without duplicating governance?**

I would project the existing approved tool registry into Foundry-facing registration metadata. That way tool name, description, owner, risk level, approval requirement, required entities, schemas, and endpoint settings all come from the governed catalog instead of being copied into a second list that can drift.

**Q: How do you know the Foundry preparation is still valid as the project changes?**

I added readiness checks for the local Foundry agent definition and tool registration metadata. They verify that the instruction file exists, the agent definition still points to MCP and Logic Apps, all approved tools are represented, and high-risk metadata still requires approval.

**Q: How do you prevent prompt or instruction drift from bypassing governance?**

The instructions are only one layer of defense. The actual enforcement still lives in code: the approved tool registry, required-entity validation, risk policy, approval checks, MCP request builder, and executor boundary. Even if an agent response is imperfect, the backend should still block unsupported tools, missing entities, and high-risk execution without approval.

## MCP And Tool Governance

**Q: Why use MCP as the backend execution boundary?**

MCP gives the agent a stable and governed way to interact with enterprise actions. Instead of calling ERP, ServiceNow, or Logic Apps internals directly, the agent calls approved tools with known contracts, risk levels, owners, and required entities.

**Q: What is in a tool contract?**

Each tool contract includes the tool name, description, business domain, backend system, risk level, approval requirement, owner, version, operational impact, required entities, and schema references.

**Q: How do required entities work?**

Required entities are defined in the tool contract. Before execution, the MCP request builder checks that those values were extracted from the user request. If something like `order_id`, `shipment_id`, or `invoice_id` is missing, execution is blocked and the response tells the caller what is needed.

**Q: How does the MCP envelope look?**

The Logic Apps workflows accept a common envelope:

```json
{
  "server_name": "logic-apps-standard-mcp",
  "tool_name": "getOrderStatus",
  "correlation_id": "abc-123",
  "payload": {
    "order_id": "ORD-1001"
  },
  "timeout_seconds": 30
}
```

This makes every backend workflow receive a predictable request shape.

**Q: How are tool endpoints configured?**

The project supports per-tool endpoint settings such as `MCP_TOOL_ENDPOINT_GET_ORDER_STATUS` and `MCP_TOOL_ENDPOINT_CHECK_SHIPMENT_STATUS`. The MCP executor selects the endpoint based on the chosen tool, with `MCP_SERVER_URL` available as a fallback.

## Logic Apps Integration

**Q: Why did you use Logic Apps for the backend workflows?**

Logic Apps is a strong fit for enterprise integration because it can orchestrate connectors, APIs, approvals, and system workflows. In this project, each Logic Apps workflow represents an approved backend action exposed through the MCP boundary.

**Q: Are the Logic Apps workflows acting as MCP tools?**

Yes, in the local implementation each workflow acts as a tool endpoint. The agent selects a tool from the registry, and the MCP executor calls that workflow's configured HTTP trigger URL using the common MCP envelope.

**Q: Why use local Logic Apps instead of deploying immediately to Azure?**

Local Logic Apps lets us prove the contract, workflow behavior, correlation IDs, and agent-to-MCP execution path without paying for a hosted Logic Apps Standard plan. Once the local flow is stable, the same pattern can move to Azure.

**Q: What workflows are currently modeled?**

The project includes order status, shipment status, invoice validation, integration run-status lookup, supplier notification, ServiceNow ticket creation, and approval request creation.

**Q: How do you handle local Logic Apps authentication?**

Local callback URLs include a `sig` query-string token. For that local path, `MCP_API_KEY` stays empty so the remote MCP client does not send an extra bearer token that the local Logic Apps runtime may reject.

## Risk And Approval

**Q: How do you decide whether a tool can execute directly?**

Each tool has a risk level. Low and medium-risk read-only or validation workflows can execute when required entities are present. High-risk tools, such as supplier notifications and ServiceNow ticket creation, require approval.

**Q: What happens when a user asks for a high-risk action?**

The agent can plan the action and extract entities, but it does not execute the tool directly. It returns `approval_required` and creates a pending approval request. The backend workflow can run only through the approved execution path.

**Q: Why not let the agent decide approval by itself?**

Approval is a business control, not a model preference. High-risk actions may affect suppliers, tickets, operations, or external communications, so a human or policy-controlled approval step is required before execution.

**Q: How does approved execution work?**

The system checks that an approval request exists, that a reviewer approved it, and that the requested tool is valid. Only then does it call the MCP execution path for the high-risk tool.

## Foundry And Evaluation

**Q: Where does Microsoft Foundry fit in this architecture?**

Foundry is the future agent runtime and governance plane. It can host or orchestrate the agent, store/version instructions, attach tools, run evaluations, capture traces, and support operational readiness.

**Q: What resources are needed before creating the real Foundry agent?**

I would confirm the Foundry project endpoint, Azure tenant, subscription, resource group, Foundry account, Foundry project name, model deployment, agent name, authentication/RBAC, evaluation dataset, and observability path. Runtime values and Azure resource context are related but separate: the runtime needs endpoint and model deployment, while operations and registration need subscription, resource group, account, and project names.

**Q: Where does Microsoft Agent Framework fit?**

Microsoft Agent Framework is the agent implementation path. Foundry is the runtime and governance platform. In this project, the target is a MAF-backed agent registered in Foundry, with FastAPI still acting as the enterprise control plane and MCP remaining the backend execution boundary.

**Q: Why add a local MAF skeleton before creating the live Foundry agent?**

The skeleton lets me validate the runtime shape first: agent name, project endpoint, model deployment, instruction file, MCP boundary, and FastAPI control plane. That reduces risk before installing live SDK dependencies or creating cloud agent resources.

**Q: What did you actually create in Foundry?**

I created a real Foundry agent version named `enterprise-integration-agent:1` in the configured Foundry project. It uses the `gpt-4.1-mini` model deployment and the governed instruction file from the repo. It is active for testing, but it is not published as a production Agent Application yet.

**Q: Why install `agent-framework-foundry` and `azure-ai-projects`?**

`agent-framework-foundry` gives the project the Microsoft Agent Framework and Foundry integration path. `azure-ai-projects` gives the code an `AIProjectClient` that can create or update agent versions in the Foundry project. This keeps live Foundry operations in code instead of doing them manually in the portal.

**Q: How did you avoid accidentally creating cloud resources during tests?**

The live Foundry registration code is isolated in `foundry/live_agent.py`, and unit tests pass fake project clients into that module. Normal tests validate request shape, metadata, instructions, and preflight behavior without calling Azure.

**Q: How did you test live Foundry invocation without making every test call Azure?**

I added a small invocation helper that accepts an optional runtime agent object. Unit tests pass a fake runtime agent and verify the message, response ID, version, and response text mapping. The real `FoundryAgent` client is only created when running a live invocation manually.

**Q: How can the same FastAPI endpoint use either local planning or the live Foundry agent?**

I added `AGENT_RUNTIME_MODE`. In `local` mode, `/agent/chat` uses the existing local rule-based adapter and can reach MCP execution when policy allows it. In `foundry` mode, the same endpoint invokes the live Foundry agent version and returns the agent's planning response, but it does not execute backend tools yet.

**Q: Why is Foundry mode planning-only at this stage?**

Because backend execution still needs policy enforcement, approval checks, audit events, and MCP envelope validation. Until the Foundry tool attachment pattern is finalized, FastAPI remains the enforcement point and Foundry mode is used to validate real agent reasoning safely.

**Q: What is the difference between registering and publishing a Foundry agent?**

Registration creates or updates the agent inside the Foundry project so it can be tested with instructions, model deployment, and tools. Publishing promotes a tested agent version into an Agent Application with a stable invocation endpoint, RBAC, and deployment lifecycle. I would register and test first, then publish later.

**Q: What is the difference between a code-owned MAF agent and the Foundry agent version?**

The code-owned MAF pieces define how the project wants the agent to behave: instructions, governance, MCP boundaries, and adapter code. The Foundry agent version is the cloud-side version of that behavior inside the Foundry project. The code is still the source of truth; Foundry gives us managed runtime, versioning, evaluation, and operations.

**Q: Why keep Foundry code isolated?**

SDKs and runtime patterns can evolve. By isolating Foundry-specific code behind an adapter boundary, the FastAPI routes, MCP layer, risk policy, and Logic Apps workflows remain stable even when the agent runtime changes.

**Q: What would you evaluate before releasing the agent?**

I would evaluate tool selection accuracy, missing-entity handling, high-risk approval gating, unsupported request behavior, correlation ID propagation, and response consistency. These local evaluation cases can later become Foundry evaluation datasets.

**Q: What should be traced in Foundry?**

At minimum: user request received, selected tool, extracted entities, risk decision, approval request or decision, MCP call, Logic Apps response, and final agent response. The shared correlation ID should connect these events.

## Observability And Operations

**Q: How do you make the workflow auditable?**

The project records audit events with correlation IDs. It can project those audit events into Foundry-style traces and Application Insights-style custom events, which makes planning, approval, and execution reviewable.

**Q: What operational readiness checks are useful?**

Useful checks include tool registry availability, risk policy availability, approval store availability, MCP runtime mode, endpoint configuration, Foundry settings, and observability settings.

**Q: What would you monitor in production?**

I would monitor failed tool calls, missing entity rates, approval-required rates, approval rejections, Logic Apps failures, timeout rates, tool latency, high-risk execution counts, and correlation IDs for support investigations.

**Q: How do you avoid leaking secrets?**

Secrets are not returned from diagnostics. The API only exposes whether an API key is configured, not the value. In Azure, secrets should move to Key Vault, managed identity, APIM policies, or platform configuration.

## Testing

**Q: What kinds of tests does the project include?**

The tests cover tool registry contracts, risk decisions, entity validation, MCP request building, remote HTTP client behavior, response normalization, approval gating, audit behavior, environment validation, Logic Apps contract shape, and agent flow behavior.

**Q: What is an important safety test?**

One important test verifies that a high-risk tool with all required entities still does not execute directly from chat. That proves readiness is not enough; risk policy must allow execution or require approval.

**Q: How do you test remote MCP without a live endpoint?**

The Python tests use `httpx.MockTransport` to simulate remote HTTP responses, authentication failures, timeouts, and backend errors without making real network calls.

**Q: How did you test the local Logic Apps bridge?**

I ran the Logic Apps Standard project locally, fetched each workflow callback URL, posted MCP envelopes directly to the workflows, and verified that the agent could call low-risk workflows through the remote MCP path. For high-risk workflows, I verified direct backend calls work but chat still requires approval.

## Azure Deployment

**Q: Why not deploy to Azure immediately?**

Logic Apps Standard on a workflow plan can incur cost even with low traffic. For this learning project, local execution proves the architecture first. Azure deployment should happen after resource names, cost, monitoring, and security are reviewed.

**Q: What would be required for Azure deployment?**

For Logic Apps Standard, the minimum deployment needs a resource group, Logic App Standard app, Workflow Standard plan, and storage account. Optional production resources include Application Insights, Log Analytics, Key Vault, APIM, and Service Bus.

**Q: How would this change in Azure?**

The workflow endpoints would become Azure-hosted URLs, secrets would move out of local settings, monitoring would use Azure services, and tool registration could be connected to Foundry, APIM, or an MCP-compatible server layer.

**Q: Would you use APIM?**

For production, APIM can be useful for policy enforcement, subscription keys, OAuth, throttling, logging, and a cleaner enterprise API boundary in front of Logic Apps. It is not required for the local proof of concept.

## Design Tradeoffs

**Q: Why start with a local rule-based agent instead of a real LLM agent?**

It makes the governance path transparent and testable first. Once the contracts, risk policy, approval gates, and MCP execution path are stable, the rule-based planner can be replaced with a Foundry-hosted agent.

**Q: Why use FastAPI if Foundry will host the agent later?**

FastAPI is the enterprise API boundary for clients, diagnostics, readiness, approvals, and integration with other services. Foundry can become the agent runtime behind that boundary without forcing callers to change.

**Q: If you use a Foundry Agent and chatbot UI, why keep FastAPI?**

FastAPI remains the enterprise control plane. The chatbot can send user requests to FastAPI, FastAPI can call the Foundry Agent for reasoning, and backend execution still goes through governed MCP tools and Logic Apps. This keeps API contracts, approvals, audit events, readiness checks, diagnostics, and secret handling outside the chatbot.

The pattern is:

```text
Chatbot UI
  -> FastAPI control plane
    -> Foundry Agent
      -> MCP tools
        -> Logic Apps workflows
```

For a small demo, the chatbot could call Foundry directly. For enterprise integration, FastAPI is stronger because final enforcement remains in backend code: unsupported tools are blocked, missing entities are rejected, high-risk actions require approval, and Logic Apps callback URLs or API keys are never exposed to the UI.

**Q: Why not let Logic Apps own all governance?**

Logic Apps is strong for workflow execution, but agent governance also needs tool selection controls, entity validation, risk decisions, approval state, audit events, and evaluation hooks before the workflow is called.

**Q: What would you improve next?**

I would decide the real Foundry project and model deployment, create the actual Foundry agent, attach the MCP tool layer, add persistent approval/audit storage, and then plan Azure deployment.

## Resume Answers

**Q: How would you describe this project on a resume?**

Built an enterprise integration modernization prototype using FastAPI, Microsoft Foundry-oriented agent architecture, governed MCP tool contracts, Logic Apps workflow endpoints, risk-based approval controls, correlation-aware audit events, and tested remote MCP execution.

**Q: What technical skills does this demonstrate?**

Python, FastAPI, agent architecture, MCP-style tool execution, Azure Logic Apps Standard, enterprise integration patterns, risk governance, approval workflows, testing, environment validation, and Azure-ready design.

**Q: What architecture skills does this demonstrate?**

Separation of planning and execution, contract-first integration design, policy-driven tool execution, backend abstraction, auditability, operational readiness, and phased migration from local proof of concept to Azure deployment.
