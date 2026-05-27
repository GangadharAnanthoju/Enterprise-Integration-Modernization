# CODEX.md

# Coding Instructions for AI-Ready Enterprise Integration Modernization Platform

## 1. Purpose

This file gives Codex clear implementation instructions for building the 4-month project:

**AI-Ready Enterprise Integration Modernization Platform using Microsoft Agent Framework, Microsoft Foundry, and Azure Logic Apps MCP Server**

Codex should generate production-style code, scripts, infrastructure templates, tests, and documentation for a working portfolio/demo solution.

The solution must use Microsoft Agent Framework as the agent development framework. Do not position Azure OpenAI as the main framework. Microsoft Foundry must be treated as a first-class platform layer for model hosting, agent operations, evaluation, and governance. MCP remains the primary enterprise execution channel for backend actions.

## 2. Core Architecture

```text
User / Web UI / VS Code MCP Client
        |
        v
Agent API built with Microsoft Agent Framework
  |
  +--> Microsoft Foundry Project (model/deployment/agent runtime)
  |       +--> evaluation and tracing
  |       +--> safety and governance policies
  |
  v
AIProjectClient / Foundry Agent integration layer
        |
        v
MCP Client Adapter
        |
        v
Azure Logic Apps Standard Remote MCP Server
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
Azure Integration Services
        |
        +--> Azure Functions
        +--> Service Bus
        +--> API Management
        +--> Storage / SQL / Cosmos DB
        +--> Application Insights / Log Analytics
        +--> Foundry observability export (evaluation and run telemetry)
```

## 3. Coding Priorities

Build in this order:

1. Repository scaffold
2. Foundry project integration baseline (config, model selection, governance hooks)
3. Agent API skeleton
4. MCP client adapter
5. Tool registry and tool metadata
6. Risk classification logic
7. Mock tools and test data
8. Azure Function validators
9. Logic Apps workflow placeholders/templates
10. Telemetry and correlation
11. Approval workflow simulation
12. CI/CD pipeline
13. Documentation and demo scripts

Do not attempt to build everything in one file. Use clean modular structure.

---

## 4. Required Repository Structure

Generate code into this structure:

```text
ai-ready-integration-platform/
│
├── README.md
├── CLAUDE.md
├── CODEX.md
├── .gitignore
├── .env.example
│
├── agent/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── agent_app.py
│   │   ├── models.py
│   │   ├── foundry/
│   │   │   ├── client_factory.py
│   │   │   ├── governance.py
│   │   │   ├── evaluations.py
│   │   │   └── tracing.py
│   │   ├── prompts/
│   │   │   ├── system_prompt.md
│   │   │   └── tool_policy.md
│   │   ├── mcp/
│   │   │   ├── client.py
│   │   │   ├── schemas.py
│   │   │   └── exceptions.py
│   │   ├── tools/
│   │   │   ├── registry.py
│   │   │   ├── risk_policy.py
│   │   │   └── contracts.py
│   │   ├── telemetry/
│   │   │   ├── correlation.py
│   │   │   ├── logging.py
│   │   │   └── appinsights.py
│   │   └── api/
│   │       ├── routes.py
│   │       └── schemas.py
│   └── tests/
│       ├── test_risk_policy.py
│       ├── test_tool_registry.py
│       ├── test_correlation.py
│       ├── test_agent_flow.py
│       ├── test_contracts.py
│       ├── test_foundry_governance.py
│       └── test_foundry_agent_integration.py
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
│   ├── payload_validator/
│   ├── risk_classifier/
│   ├── transformation_helper/
│   └── correlation_helper/
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
├── infra/
│   ├── main.bicep
│   ├── parameters.dev.json
│   ├── modules/
│   │   ├── appinsights.bicep
│   │   ├── keyvault.bicep
│   │   ├── logicapp.bicep
│   │   ├── functionapp.bicep
│   │   ├── servicebus.bicep
│   │   ├── storage.bicep
│   │   └── apim.bicep
│   └── scripts/
│       ├── deploy-dev.sh
│       └── deploy-dev.ps1
│
├── test-data/
│   ├── orders.json
│   ├── invoices.json
│   ├── shipments.json
│   └── tickets.json
│
├── docs/
│   ├── architecture.md
│   ├── tool-catalog.md
│   ├── security-design.md
│   ├── monitoring.md
│   ├── foundry-governance.md
│   ├── runbook.md
│   ├── deployment-guide.md
│   └── demo-script.md
│
└── pipelines/
    ├── azure-pipelines.yml
    └── github-actions.yml
```

  ---

  ## 4A. Version Freshness and Release Alignment

  Microsoft Agent Framework moved quickly in 2026. Always validate current package/API guidance before coding and before release.

  Required checks for every development sprint:

  1. Re-check official Microsoft Agent Framework guidance and Foundry agent patterns.
  2. Re-check package versions and prerelease requirements.
  3. Keep framework-specific logic isolated under `agent/src/foundry/` and `agent/src/agent_app.py`.
  4. Record version decisions in `foundry/governance/release-checklist.md`.

  Implementation rule:

  - Use Microsoft Foundry agent patterns (`AIProjectClient`) for hosted agent runtime.
  - Use MCP tools for enterprise actions; do not bypass MCP for SAP, ServiceNow, partner APIs, or messaging actions.

---

## 5. Agent Service Requirements

### Technology

Use Python unless explicitly requested otherwise.

Required packages may include:

```text
agent-framework
fastapi
uvicorn
pydantic
pydantic-settings
azure-identity
azure-keyvault-secrets
azure-monitor-opentelemetry
opentelemetry-api
opentelemetry-sdk
httpx
python-dotenv
pytest
pytest-asyncio
ruff
```

If the Microsoft Agent Framework package name or import path changes, isolate framework-specific code in `agent_app.py` so the rest of the solution remains stable.

### API Endpoints

Implement the following FastAPI endpoints:

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/agent/chat` | Submit user message to agent |
| GET | `/tools` | Return local tool catalog metadata |
| GET | `/tools/{tool_name}` | Return tool metadata |
| POST | `/tools/{tool_name}/simulate` | Optional local simulation for testing |

### Request Model

```python
class AgentChatRequest(BaseModel):
    user_message: str
    user_id: str | None = None
    session_id: str | None = None
    correlation_id: str | None = None
```

### Response Model

```python
class AgentChatResponse(BaseModel):
    response_text: str
    session_id: str
    correlation_id: str
    tool_calls: list[ToolCallSummary] = []
    approval_required: bool = False
    approval_id: str | None = None
```

---

## 6. Tool Registry Requirements

Create `agent/src/tools/registry.py` with static metadata for tools.

Each tool must have:

```python
class ToolMetadata(BaseModel):
    name: str
    description: str
    business_domain: str
    backend_system: str
    risk_level: Literal["Low", "Medium", "High"]
    approval_required: bool
    input_schema_ref: str
    output_schema_ref: str
    owner: str
```

Required tools:

1. `getOrderStatus`
2. `validateInvoice`
3. `checkShipmentStatus`
4. `sendSupplierNotification`
5. `createApprovalRequest`
6. `createServiceNowTicket`
7. `queryIntegrationRunStatus`
8. `submitPartnerMessage`

---

## 7. Risk Policy Requirements

Create `agent/src/tools/risk_policy.py`.

Rules:

```text
Low risk:
- Read-only status lookup
- Query order status
- Query shipment status
- Query integration run status

Medium risk:
- Create ServiceNow ticket
- Send internal notification
- Validate invoice

High risk:
- Send supplier notification
- Submit partner/B2B message
- Update SAP/ERP data
- Update financial/invoice data
```

Function requirements:

```python
def requires_approval(tool_name: str) -> bool:
    ...

def classify_risk(tool_name: str) -> RiskLevel:
    ...

def validate_execution_allowed(tool_name: str, approval_status: str | None) -> None:
    ...
```

If approval is required and not approved, raise a custom `ApprovalRequiredError`.

---

## 8. MCP Client Adapter Requirements

Create `agent/src/mcp/client.py`.

Responsibilities:

- Connect to remote MCP server endpoint.
- List available tools, if supported.
- Invoke a named tool with JSON payload.
- Add correlation ID header or payload field.
- Add API key or bearer token as configured.
- Convert errors into structured `McpToolError`.

Interface:

```python
class McpClient:
    def __init__(self, settings: Settings):
        ...

    async def list_tools(self) -> list[dict]:
        ...

    async def call_tool(
        self,
        tool_name: str,
        payload: dict,
        correlation_id: str,
    ) -> dict:
        ...
```

For local development, support a `MOCK_MCP=true` mode that uses JSON test data instead of calling Azure.

---

## 9. Agent Orchestration Requirements

Create `agent/src/agent_app.py`.

Responsibilities:

1. Initialize Microsoft Agent Framework agent.
2. Load system prompt.
3. Register tool invocation adapter.
4. Handle user message.
5. Decide whether tool calls are allowed.
6. Call MCP tools through `McpClient`.
7. Return business-friendly response.
8. Include correlation ID in every response.

Agent instructions must include:

```text
You are an enterprise integration assistant.
You must use approved MCP tools for enterprise actions.
You must not invent backend data.
You must require approval for high-risk actions.
You must summarize results clearly for operations and support teams.
You must include correlation ID in the final response.
```

---

## 10. Tool Contracts

Create JSON schema files under `agent/src/tools/contracts.py` or `docs/tool-catalog.md`.

### getOrderStatus Input

```json
{
  "orderNumber": "4500098123",
  "sourceSystem": "SAP"
}
```

### getOrderStatus Output

```json
{
  "orderNumber": "4500098123",
  "status": "In Transit",
  "estimatedDeliveryDate": "2026-05-21",
  "delayRisk": "Medium",
  "correlationId": "abc-123"
}
```

### validateInvoice Input

```json
{
  "invoiceNumber": "INV-10092",
  "vendorId": "VEND-2001",
  "poNumber": "4500098123",
  "invoiceAmount": 12500.75
}
```

### validateInvoice Output

```json
{
  "invoiceNumber": "INV-10092",
  "validationStatus": "Passed",
  "matchedPO": true,
  "taxValidation": "Passed",
  "requiresApproval": false,
  "correlationId": "abc-123"
}
```

### createServiceNowTicket Output

```json
{
  "ticketNumber": "INC0012345",
  "status": "Created",
  "assignmentGroup": "Integration Support",
  "correlationId": "abc-123"
}
```

---

## 11. Telemetry Requirements

Create telemetry helper methods.

Each request must log:

```json
{
  "eventType": "McpToolExecution",
  "correlationId": "abc-123",
  "sessionId": "session-001",
  "toolName": "getOrderStatus",
  "riskLevel": "Low",
  "approvalRequired": false,
  "approvalStatus": "NotRequired",
  "executionStatus": "Succeeded",
  "durationMs": 342,
  "backendSystem": "SAP",
  "businessTransactionId": "4500098123"
}
```

Use structured logging first. Add Application Insights integration behind an abstraction so local development still works without Azure.

---

## 12. Mock Mode Requirements

The project must run without Azure by setting:

```env
MOCK_MCP=true
```

In mock mode:

- `getOrderStatus` reads from `test-data/orders.json`
- `validateInvoice` reads from `test-data/invoices.json`
- `checkShipmentStatus` reads from `test-data/shipments.json`
- `createServiceNowTicket` appends or simulates from `test-data/tickets.json`
- `sendSupplierNotification` returns simulated sent status
- `createApprovalRequest` returns simulated pending approval

This is critical so the project can be demonstrated locally.

---

## 13. Test Data Requirements

### orders.json

```json
[
  {
    "orderNumber": "4500098123",
    "customerName": "Contoso Retail",
    "status": "In Transit",
    "estimatedDeliveryDate": "2026-05-21",
    "delayRisk": "Medium"
  },
  {
    "orderNumber": "4500098124",
    "customerName": "Northwind Traders",
    "status": "Delayed",
    "estimatedDeliveryDate": "2026-05-27",
    "delayRisk": "High"
  }
]
```

### invoices.json

```json
[
  {
    "invoiceNumber": "INV-10092",
    "poNumber": "4500098123",
    "vendorId": "VEND-2001",
    "invoiceAmount": 12500.75,
    "expectedAmount": 12500.75,
    "taxValidation": "Passed",
    "duplicate": false
  }
]
```

### shipments.json

```json
[
  {
    "orderNumber": "4500098123",
    "carrier": "Global Freight",
    "trackingNumber": "TRK-90001",
    "shipmentStatus": "In Transit",
    "eta": "2026-05-21",
    "delayRisk": "Medium"
  }
]
```

---

## 14. Azure Functions Requirements

Create placeholders or working functions for:

### payload_validator

- Validates incoming payload against schema.
- Returns validation errors.

### risk_classifier

- Accepts tool name and payload.
- Returns risk level and approval requirement.

### transformation_helper

- Converts internal canonical payload to backend API payload.
- Converts backend response to canonical response.

### correlation_helper

- Generates or validates correlation IDs.
- Ensures correlation ID exists in every message.

---

## 15. Logic Apps Workflow Requirements

For each workflow folder, include:

```text
workflow.json
README.md
sample-request.json
sample-response.json
```

Workflow folders:

1. `getOrderStatus`
2. `validateInvoice`
3. `checkShipmentStatus`
4. `sendSupplierNotification`
5. `createApprovalRequest`
6. `createServiceNowTicket`
7. `queryIntegrationRunStatus`

Each Logic App should:

- Accept JSON input.
- Validate required fields.
- Add or preserve correlation ID.
- Call backend/mock endpoint or Service Bus.
- Return structured JSON output.
- Log tracked properties.

---

## 16. Infrastructure Requirements

Use Bicep modules for:

1. Resource Group assumptions
2. Storage Account
3. Logic Apps Standard
4. Function App
5. Service Bus
6. Key Vault
7. Application Insights
8. Log Analytics
9. API Management optional
10. API Center optional

Do not hard-code environment names. Use parameters.

Required parameters:

```json
{
  "environmentName": "dev",
  "location": "eastus",
  "projectPrefix": "aiint",
  "tags": {
    "Project": "AI-Ready Integration Modernization",
    "Owner": "Integration Team",
    "Environment": "dev"
  }
}
```

---

## 17. CI/CD Requirements

Create either Azure DevOps or GitHub Actions, preferably both templates.

Pipeline stages:

1. Validate
2. Build
3. Test
4. Deploy Infrastructure
5. Deploy Functions
6. Deploy Logic Apps
7. Deploy Agent API
8. Smoke Test

### Validation Commands

```bash
python -m pip install -r agent/requirements.txt
pytest agent/tests
ruff check agent/src agent/tests
az bicep build --file infra/main.bicep
```

---

## 18. Documentation Requirements

Generate these documents:

### docs/architecture.md

Include:

- Architecture overview
- Component responsibilities
- Main data flows
- Security flows
- Monitoring flows

### docs/tool-catalog.md

Include:

- Tool names
- Inputs
- Outputs
- Risk levels
- Approval requirements
- Backend systems

### docs/security-design.md

Include:

- Entra ID
- Easy Auth
- Managed Identity
- Key Vault
- RBAC
- Approval model
- Audit model

### docs/monitoring.md

Include:

- App Insights events
- KQL queries
- Dashboard metrics
- Alert rules

### docs/runbook.md

Include:

- Failed MCP tool call troubleshooting
- Service Bus dead-letter replay
- Approval workflow troubleshooting
- Secret rotation
- Adding a new tool

### docs/demo-script.md

Include:

- Demo setup
- Demo scenario steps
- Expected response examples
- Troubleshooting tips

---

## 19. Demo Script Requirements

Implement or document these prompts:

### Prompt 1

```text
Check order 4500098123 and tell me if shipment is delayed.
```

Expected tool calls:

1. `getOrderStatus`
2. `checkShipmentStatus`

### Prompt 2

```text
Check order 4500098124. If delayed, notify supplier and create a ServiceNow ticket.
```

Expected tool calls:

1. `getOrderStatus`
2. `checkShipmentStatus`
3. `createApprovalRequest`
4. `sendSupplierNotification`, after approval
5. `createServiceNowTicket`

### Prompt 3

```text
Validate invoice INV-10092 against PO 4500098123.
```

Expected tool calls:

1. `validateInvoice`

### Prompt 4

```text
Check failed integration run RUN-90001 and create a ticket if needed.
```

Expected tool calls:

1. `queryIntegrationRunStatus`
2. `createServiceNowTicket`, if failure found

---

## 20. Error Handling Requirements

All errors must follow this structure:

```json
{
  "errorCode": "BACKEND_TIMEOUT",
  "message": "Shipment API did not respond within expected time.",
  "toolName": "checkShipmentStatus",
  "correlationId": "abc-123",
  "retryable": true,
  "recommendedAction": "Retry or route to ServiceNow ticket creation."
}
```

Define error categories:

- `VALIDATION_ERROR`
- `AUTHENTICATION_ERROR`
- `AUTHORIZATION_ERROR`
- `APPROVAL_REQUIRED`
- `BACKEND_TIMEOUT`
- `BACKEND_FAILURE`
- `MCP_SERVER_ERROR`
- `UNKNOWN_ERROR`

---

## 21. Security Requirements

- Never store secrets in code.
- Never print API keys or tokens in logs.
- Use Key Vault for secrets.
- Use Managed Identity for Azure resource access.
- Use Entra ID/Easy Auth for protected endpoints.
- Use tool-level risk policy before execution.
- Approval must be mandatory for high-risk tools.
- Log all high-risk requests and approval decisions.

---

## 22. Local Development Commands

Suggested commands:

```bash
cd agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
export MOCK_MCP=true
uvicorn src.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Agent chat:

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Check order 4500098123 and tell me if shipment is delayed.",
    "user_id": "demo-user"
  }'
```

---

## 23. Definition of Done for Codex

Codex should consider the implementation complete when it has generated:

1. Working FastAPI agent shell.
2. Microsoft Agent Framework integration placeholder or actual implementation.
3. MCP client adapter with mock mode.
4. Tool registry with metadata.
5. Risk and approval policy.
6. Mock test data.
7. Unit tests.
8. Azure Function placeholders.
9. Logic Apps workflow placeholders.
10. Bicep infrastructure baseline.
11. CI/CD pipeline templates.
12. Docs for architecture, security, monitoring, runbook, and demo.
13. README with setup instructions.

---

## 24. Important Implementation Notes

- Keep the project demo-friendly.
- Mock mode must work even without Azure access.
- Azure deployment should be optional but documented.
- Keep code clean and modular.
- Prefer realistic enterprise naming.
- Use correlation IDs everywhere.
- Keep risk and approval logic explicit.
- Make the solution look like an enterprise integration architect built it, not a simple chatbot demo.

