# CLAUDE.md

# Project: AI-Ready Enterprise Integration Modernization Platform

## 1. Project Goal

Build a 4-month proof-of-delivery project that demonstrates how enterprise Azure Integration Services workflows can be modernized into AI-callable, governed tools using:

- Microsoft Agent Framework
- Microsoft Foundry (agent runtime, model operations, evaluation, and governance)
- Azure Logic Apps Standard as Remote MCP Server
- Azure API Management
- Azure API Center / Tool Catalog
- Azure Service Bus
- Azure Functions
- Microsoft Entra ID / Easy Auth
- Managed Identity
- Azure Key Vault
- Application Insights / Log Analytics
- Power BI operational reporting
- Azure DevOps / GitHub Actions

The project should avoid positioning the solution as a simple chatbot. The goal is to show a production-style enterprise integration modernization pattern where Microsoft Agent Framework orchestrates approved MCP tools backed by Logic Apps workflows, while Microsoft Foundry provides hosted AI runtime and governance controls.

## 2. Executive Summary

This project modernizes reusable enterprise workflows into governed MCP tools that can be discovered and invoked by an agent built with Microsoft Agent Framework and operated in Microsoft Foundry. The agent does not directly access SAP, ServiceNow, databases, partner APIs, or messaging platforms. Instead, it calls approved Logic Apps Standard MCP tools that enforce validation, security, observability, and approval controls.

The platform demonstrates agentic workflows for:

1. Order status lookup
2. Invoice validation
3. Shipment status check
4. Supplier notification
5. ServiceNow ticket creation
6. Approval-based execution for high-risk actions
7. Integration run-status lookup for support teams
8. Operational monitoring and reporting

## 3. 4-Month Delivery Plan

### Month 1: Foundation, Architecture, and MCP Baseline

#### Objectives

- Finalize target architecture.
- Create source control repository and project structure.
- Create Azure resource baseline.
- Configure Logic Apps Standard as a remote MCP server.
- Build first 2 MCP workflow tools.
- Build Microsoft Agent Framework local agent shell.
- Validate end-to-end MCP tool invocation from development client.

#### Development Tasks

1. Create repository structure.
2. Define environment naming standards.
3. Create infrastructure baseline using Bicep or Terraform.
4. Provision development resources:
   - Resource Group
   - Logic Apps Standard
   - Storage Account
   - Key Vault
   - Application Insights
   - Log Analytics Workspace
   - Service Bus Namespace
   - Azure Functions
   - API Management developer tier or consumption-friendly alternative
   - API Center, if available
5. Configure Logic Apps Standard for MCP tool hosting.
6. Create initial MCP server grouping:
   - `order-tools`
   - `invoice-tools`
   - `support-tools`
7. Implement first tools:
   - `getOrderStatus`
   - `validateInvoice`
8. Build Microsoft Agent Framework agent application.
9. Add MCP client connection logic.
10. Validate local execution.
11. Add basic App Insights telemetry.

#### Deliverables

- Architecture diagram
- Git repository
- Infrastructure deployment scripts
- Initial Logic Apps MCP server
- 2 working MCP tools
- Microsoft Agent Framework console or API agent
- Initial README
- Basic test data

#### Acceptance Criteria

- Developer can run the agent locally.
- Agent can connect to Logic Apps MCP server.
- Agent can call `getOrderStatus` and `validateInvoice`.
- Tool responses are returned in structured JSON.
- Tool execution is visible in Application Insights.

---

### Month 2: Business Tool Expansion and Integration Layer

#### Objectives

- Expand the MCP tool catalog.
- Add asynchronous integration using Service Bus.
- Add Azure Functions for custom validation and transformation.
- Add supplier notification and ServiceNow mock integration.
- Add tool contracts and schema validation.

#### Development Tasks

1. Add additional Logic Apps MCP tools:
   - `checkShipmentStatus`
   - `sendSupplierNotification`
   - `createServiceNowTicket`
   - `queryIntegrationRunStatus`
2. Create mock backend services:
   - Mock SAP/order API
   - Mock shipment API
   - Mock ServiceNow endpoint or sandbox connector
3. Create Service Bus queues/topics:
   - `agent-requests`
   - `supplier-notifications`
   - `ticket-events`
   - `approval-events`
   - `deadletter-replay`
4. Build Azure Function components:
   - Payload validator
   - Transformation helper
   - Risk classification helper
   - Correlation ID helper
5. Add input/output JSON schemas for each tool.
6. Add consistent error response format.
7. Add retry and dead-letter behavior.
8. Add agent-side tool selection instructions.
9. Add integration test scripts.

#### Deliverables

- 6 working MCP tools
- Service Bus integration
- Azure Functions for validation/transformation
- JSON schemas
- Mock backend services
- Integration test collection
- Tool catalog markdown

#### Acceptance Criteria

- Agent can execute order, shipment, invoice, notification, ticket, and run-status scenarios.
- All tools return consistent JSON responses.
- Correlation ID is propagated across agent, MCP workflow, Service Bus, Functions, and logs.
- Failed messages are routed to dead-letter handling.

---

### Month 3: Governance, Security, Approval, and Observability

#### Objectives

- Add enterprise-grade guardrails.
- Add human-in-the-loop approval for high-risk actions.
- Add authentication and authorization controls.
- Add operational dashboards and KQL queries.
- Add API Center/tool catalog governance.

#### Development Tasks

1. Configure Microsoft Entra ID authentication.
2. Configure Easy Auth for Logic Apps MCP endpoints.
3. Configure Managed Identity access to Key Vault, Storage, Service Bus, and App Insights.
4. Store secrets in Key Vault.
5. Add tool-level authorization model.
6. Add risk classification:
   - Low risk: read-only lookup
   - Medium risk: ticket or notification
   - High risk: external message, backend update, financial or supplier action
7. Implement approval workflow:
   - Create approval request
   - Wait for approval
   - Continue or reject execution
   - Audit decision
8. Add audit logging:
   - Agent session ID
   - User request ID
   - Tool name
   - Risk level
   - Approval status
   - Backend system
   - Execution status
9. Register tools in API Center / Tool Catalog.
10. Add APIM policies if APIM is used in front of MCP endpoints.
11. Create KQL queries for:
   - Tool usage
   - Failed runs
   - Approval statistics
   - Latency
   - Agent sessions
   - Backend dependency failures
12. Create Power BI dataset or CSV export model.

#### Deliverables

- Security design
- Tool authorization matrix
- Human approval flow
- Audit log schema
- KQL query library
- Operational dashboard specification
- API Center/tool catalog entries

#### Acceptance Criteria

- High-risk tools cannot execute without approval.
- Unauthorized clients cannot access MCP endpoints.
- All tool calls are logged with correlation ID.
- Dashboard shows tool usage, failures, approval status, and SLA indicators.

---

### Month 4: End-to-End Scenarios, Hardening, Documentation, and Demo

#### Objectives

- Complete end-to-end demo scenarios.
- Harden error handling and retry logic.
- Complete DevOps pipelines.
- Create documentation and resume/portfolio artifacts.
- Prepare final demonstration.

#### Development Tasks

1. Complete main demo scenarios:
   - Order delay scenario
   - Invoice validation exception scenario
   - ServiceNow incident creation scenario
   - Integration support troubleshooting scenario
2. Add automated tests:
   - Unit tests for functions
   - Contract tests for tools
   - Agent prompt/tool execution tests
   - End-to-end tests
3. Add CI/CD pipelines:
   - Build agent app
   - Deploy infrastructure
   - Deploy Logic Apps workflows
   - Deploy Azure Functions
   - Deploy APIM policies
   - Run tests
4. Add environment parameterization:
   - Dev
   - QA
   - UAT/demo
5. Add runbooks:
   - How to onboard a new MCP tool
   - How to troubleshoot failed tool call
   - How to replay failed Service Bus message
   - How to rotate secrets
   - How to monitor agent activity
6. Add final documentation.
7. Add architecture diagram and sequence diagrams.
8. Prepare resume bullets and project summary.

#### Deliverables

- Final source code
- CI/CD pipelines
- Deployment guide
- Tool onboarding guide
- Operations runbook
- Architecture diagram
- Demo script
- Resume-ready project description

#### Acceptance Criteria

- Project can be deployed into a fresh Azure environment using documented steps.
- Demo scenarios execute successfully.
- Logs and dashboards show complete traceability.
- Approval workflow works for high-risk actions.
- README and runbooks are complete.

---

## 4. Target Architecture

```text
Business User / Support User / Developer
        |
        v
Copilot-style UI / Custom Web UI / VS Code MCP Client
        |
        v
Microsoft Agent Framework Agent
   |
   +--> Microsoft Foundry Project
   |       +--> model hosting and deployment
   |       +--> agent runtime and threads
   |       +--> evaluation, tracing, and governance
   |
        |
        v
MCP Client Layer
        |
        v
Azure Logic Apps Standard as Remote MCP Server
        |
        +--> getOrderStatus
        +--> validateInvoice
        +--> checkShipmentStatus
        +--> sendSupplierNotification
        +--> createApprovalRequest
        +--> createServiceNowTicket
        +--> queryIntegrationRunStatus
        |
        v
Integration & Automation Services
        |
        +--> Azure API Management
        +--> Azure Functions
        +--> Azure Service Bus
        +--> Dataverse / SQL / Cosmos DB / Storage
        +--> Email / Teams Notifications
        +--> Approval Workflow
        +--> Transformation / Validation
        +--> Audit Logging
        |
        v
Enterprise & External Systems
        |
        +--> SAP / ERP or mock SAP API
        +--> ServiceNow or mock ticketing API
        +--> Partner APIs
        +--> B2B / EDI Systems
        +--> Customer Information System
        +--> Order / Shipment Systems

Cross-Cutting:
- Microsoft Entra ID
- Easy Auth
- Managed Identity
- Key Vault
- RBAC / tool authorization
- API Center / MCP tool catalog
- Microsoft Foundry governance and evaluations
- Application Insights
- Log Analytics
- Power BI dashboards
- Azure DevOps / GitHub Actions
```

## 5. Functional Requirements

### FR-001: Agent Conversation Interface

The solution must provide a simple interface to send user requests to the Microsoft Agent Framework application.

Minimum options:

- Console app
- FastAPI endpoint
- ASP.NET Core Web API
- Lightweight web chat UI

Recommended for this project:

- Python FastAPI agent API
- Optional React static web UI

### FR-002: Agent Tool Orchestration

The agent must understand user intent and select the correct MCP tools.

Required intents:

- Check order status
- Validate invoice
- Check shipment
- Notify supplier
- Create ticket
- Query integration run status
- Create approval request

### FR-003: MCP Tool Invocation

The agent must call tools exposed by Logic Apps Standard MCP server.

Required tools:

1. `getOrderStatus`
2. `validateInvoice`
3. `checkShipmentStatus`
4. `sendSupplierNotification`
5. `createApprovalRequest`
6. `createServiceNowTicket`
7. `queryIntegrationRunStatus`

### FR-004: Tool Contract Validation

Each tool must have:

- Tool name
- Description
- Input schema
- Output schema
- Risk level
- Owner
- Backend system
- Error response contract

### FR-005: Approval Control

High-risk actions must require approval.

Examples:

- Sending supplier notification
- Submitting B2B message
- Updating shipment status
- Updating ERP/SAP data

### FR-006: Audit Logging

Every tool execution must log:

- Correlation ID
- Agent session ID
- User request
- Tool name
- Input summary
- Output status
- Risk level
- Approval status
- Backend system
- Duration
- Error message, if any

### FR-007: Monitoring

The solution must expose monitoring through:

- Application Insights traces
- Log Analytics queries
- Dashboard specification
- Failure alerts

### FR-008: DevOps

The solution must include CI/CD for:

- Infrastructure deployment
- Agent application deployment
- Azure Function deployment
- Logic Apps workflow deployment
- APIM policy deployment, if used
- Test execution

---

## 6. Non-Functional Requirements

| Area | Requirement |
|---|---|
| Security | No secrets in code. Use Key Vault and Managed Identity. |
| Reliability | Retry transient backend failures. Dead-letter failed async messages. |
| Observability | Every transaction must have correlation ID. |
| Maintainability | Use modular project structure and reusable tool definitions. |
| Scalability | Use Service Bus for long-running and asynchronous operations. |
| Governance | Tool catalog must show risk level, owner, approval requirement, and backend system. |
| AI Governance | Foundry-hosted agent runs must be traceable, evaluable, and policy-aligned before production rollout. |
| Compliance | Audit high-risk tool calls and approval decisions. |
| Portability | Environment-specific configuration must be externalized. |

---

## 7. Suggested Repository Structure

```text
ai-ready-integration-platform/
│
├── README.md
├── CLAUDE.md
├── CODEX.md
├── docs/
│   ├── architecture.md
│   ├── tool-catalog.md
│   ├── security-design.md
│   ├── monitoring.md
│   ├── foundry-governance.md
│   ├── deployment-guide.md
│   ├── runbook.md
│   └── demo-script.md
│
├── infra/
│   ├── main.bicep
│   ├── parameters.dev.json
│   ├── parameters.qa.json
│   ├── modules/
│   │   ├── logicapp.bicep
│   │   ├── functionapp.bicep
│   │   ├── servicebus.bicep
│   │   ├── keyvault.bicep
│   │   ├── appinsights.bicep
│   │   ├── loganalytics.bicep
│   │   └── apim.bicep
│   └── scripts/
│       ├── deploy-dev.sh
│       └── deploy-dev.ps1
│
├── agent/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   ├── src/
│   │   ├── main.py
│   │   ├── agent_app.py
│   │   ├── config.py
│   │   ├── foundry/
│   │   │   ├── client_factory.py
│   │   │   ├── governance.py
│   │   │   ├── evaluations.py
│   │   │   └── tracing.py
│   │   ├── prompts/
│   │   │   ├── system_prompt.md
│   │   │   └── tool_selection_prompt.md
│   │   ├── tools/
│   │   │   ├── mcp_client.py
│   │   │   ├── tool_registry.py
│   │   │   └── risk_policy.py
│   │   ├── telemetry/
│   │   │   ├── appinsights.py
│   │   │   └── correlation.py
│   │   └── api/
│   │       └── routes.py
│   └── tests/
│       ├── test_agent.py
│       ├── test_tool_policy.py
│       ├── test_mcp_client.py
│       ├── test_foundry_governance.py
│       └── test_foundry_integration.py
│
├── foundry/
│   ├── agent-definitions/
│   │   ├── enterprise-integration-agent.yaml
│   │   └── tool-access-policy.yaml
│   ├── evaluations/
│   │   ├── datasets/
│   │   ├── evaluators/
│   │   └── baselines/
│   └── governance/
│       ├── safety-policies.md
│       ├── model-selection.md
│       └── release-checklist.md
│
├── functions/
│   ├── validators/
│   ├── transformations/
│   ├── risk-classifier/
│   └── correlation-helper/
│
├── logicapps/
│   ├── workflows/
│   │   ├── getOrderStatus/
│   │   ├── validateInvoice/
│   │   ├── checkShipmentStatus/
│   │   ├── sendSupplierNotification/
│   │   ├── createApprovalRequest/
│   │   ├── createServiceNowTicket/
│   │   └── queryIntegrationRunStatus/
│   └── connections/
│
├── apim/
│   ├── policies/
│   └── products/
│
├── test-data/
│   ├── orders.json
│   ├── invoices.json
│   ├── shipments.json
│   └── tickets.json
│
├── scripts/
│   ├── seed-test-data.py
│   ├── run-e2e-tests.py
│   └── export-dashboard-data.py
│
└── pipelines/
    ├── azure-pipelines.yml
    └── github-actions.yml
```

---

## 8. MCP Tool Catalog

| Tool Name | Purpose | Risk | Approval | Backend |
|---|---|---|---|---|
| `getOrderStatus` | Retrieve order status | Low | No | SAP/mock order API |
| `validateInvoice` | Validate invoice against PO/vendor data | Medium | No | SQL/mock invoice API |
| `checkShipmentStatus` | Retrieve shipment/ETA status | Low | No | Partner API/mock shipment API |
| `sendSupplierNotification` | Notify supplier of delay or exception | Medium | Yes | Email/Teams/Partner API |
| `createApprovalRequest` | Create human approval task | Medium | No | Logic App approval workflow |
| `createServiceNowTicket` | Create or update incident | Low/Medium | No | ServiceNow/mock API |
| `queryIntegrationRunStatus` | Query workflow run status and errors | Low | No | App Insights/Log Analytics |
| `submitPartnerMessage` | Submit outbound partner/B2B payload | High | Yes | Service Bus/B2B gateway |

---

## 9. Demo Scenarios

### Scenario 1: Order Delay Handling

User asks:

> Check order 4500098123. If delayed, notify supplier and create a ticket.

Expected flow:

1. Agent calls `getOrderStatus`.
2. Agent calls `checkShipmentStatus`.
3. Agent detects delay.
4. Agent creates approval using `createApprovalRequest`.
5. After approval, agent calls `sendSupplierNotification`.
6. Agent calls `createServiceNowTicket`.
7. Agent returns summary to user.

### Scenario 2: Invoice Validation

User asks:

> Validate invoice INV-10092 against PO 4500098123.

Expected flow:

1. Agent calls `validateInvoice`.
2. Tool validates vendor, PO, amount, tax, and duplicate invoice status.
3. If exception exists, agent calls `createServiceNowTicket`.
4. Agent returns validation result.

### Scenario 3: Integration Support Troubleshooting

User asks:

> Check failed run ID 0858xxx and tell me root cause.

Expected flow:

1. Agent calls `queryIntegrationRunStatus`.
2. Tool queries App Insights / Log Analytics.
3. Agent summarizes failure, impacted workflow, error category, and next steps.
4. Agent creates ServiceNow ticket if required.

---

## 10. Environment Variables

Create `agent/.env.example`:

```env
ENVIRONMENT=dev
AGENT_NAME=enterprise-integration-agent
FOUNDRY_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com
MODEL_DEPLOYMENT_NAME=your-model-name
FOUNDRY_AGENT_NAME=enterprise-integration-agent
FOUNDRY_EVAL_DATASET_NAME=enterprise-mcp-regression
MCP_SERVER_URL=https://your-logicapp.azurewebsites.net/runtime/webhooks/mcp/sse
MCP_API_KEY=replace-with-keyvault-reference-or-local-secret
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=replace
AZURE_TENANT_ID=replace
AZURE_CLIENT_ID=replace
KEY_VAULT_URL=https://your-kv.vault.azure.net/
SERVICE_BUS_NAMESPACE=your-sb.servicebus.windows.net
LOG_ANALYTICS_WORKSPACE_ID=replace
```

Version note: Microsoft Agent Framework and Foundry SDK components evolved rapidly in 2026. Validate current package versions and supported APIs before each sprint and before release.

Do not commit real secrets.

---

## 11. Agent Behavior Guidelines

The agent must:

1. Use MCP tools for all enterprise data/actions.
2. Never claim backend access unless a tool result confirms it.
3. Ask for required identifiers when missing, such as PO number, invoice number, or run ID.
4. Treat supplier notification, B2B submission, ERP update, and financial updates as high-risk.
5. Require approval before high-risk execution.
6. Return business-friendly summaries.
7. Include correlation ID in user-facing response for support traceability.
8. Log every tool call.
9. Never expose secrets, API keys, or full connection strings.

---

## 12. Coding Standards

- Use Python 3.11+ for the agent service.
- Use Microsoft Agent Framework packages where applicable.
- Use Azure Identity for authentication.
- Use typed request/response models with Pydantic.
- Use structured logging.
- Use correlation IDs.
- Keep tool orchestration separate from HTTP API code.
- Keep prompts in separate markdown files.
- Keep mock data in `test-data`.
- Use `pytest` for tests.
- Use `ruff` or `flake8` for linting.
- Use `mypy` if feasible.

---

## 13. Test Strategy

### Unit Tests

- Risk classification
- Tool registry lookup
- Correlation ID generation
- Agent request parsing
- Error response formatting

### Contract Tests

- MCP tool input schemas
- MCP tool output schemas
- Error schema compatibility

### Integration Tests

- Agent to MCP server
- MCP workflow to Function App
- Logic App to Service Bus
- Logic App to mock backend
- App Insights telemetry capture

### End-to-End Tests

- Order delay scenario
- Invoice validation scenario
- ServiceNow ticket creation scenario
- Run-status troubleshooting scenario

---

## 14. Monitoring and KQL Ideas

### Tool Calls by Tool Name

```kql
traces
| where timestamp > ago(24h)
| extend toolName = tostring(customDimensions.toolName)
| where isnotempty(toolName)
| summarize count() by toolName
| order by count_ desc
```

### Failed Tool Calls

```kql
traces
| where timestamp > ago(24h)
| extend toolName = tostring(customDimensions.toolName)
| extend status = tostring(customDimensions.executionStatus)
| where status in ("Failed", "Error")
| project timestamp, toolName, status, message, customDimensions
```

### Approval Metrics

```kql
traces
| where timestamp > ago(7d)
| extend approvalStatus = tostring(customDimensions.approvalStatus)
| where isnotempty(approvalStatus)
| summarize count() by approvalStatus
```

### Latency by Tool

```kql
traces
| where timestamp > ago(24h)
| extend toolName = tostring(customDimensions.toolName)
| extend durationMs = todouble(customDimensions.durationMs)
| where isnotempty(toolName)
| summarize avg(durationMs), p95=percentile(durationMs, 95) by toolName
```

---

## 15. Definition of Done

The project is complete when:

1. Agent application runs locally and in Azure-hosted environment.
2. Logic Apps Standard exposes at least 7 MCP tools.
3. Agent can call MCP tools successfully.
4. High-risk actions require approval.
5. Service Bus is used for asynchronous operations.
6. Azure Functions handle validation/transformation/risk classification.
7. App Insights and Log Analytics capture end-to-end traces.
8. CI/CD pipeline deploys infrastructure and application components.
9. Tool catalog and onboarding guide are complete.
10. At least 4 end-to-end demo scenarios are working.

---

## 16. Resume Summary for This Project

Designed and developed a 4-month AI-ready enterprise integration modernization project using Microsoft Agent Framework and Azure Logic Apps Standard as remote MCP servers. Exposed reusable workflows as governed MCP tools for order lookup, invoice validation, shipment tracking, supplier notification, approval routing, ServiceNow ticketing, and integration run-status troubleshooting. Implemented enterprise guardrails including Entra ID authentication, Easy Auth, Managed Identity, Key Vault, RBAC, tool-risk classification, human-in-the-loop approvals, Application Insights, Log Analytics, Service Bus-based asynchronous processing, and DevOps automation.
