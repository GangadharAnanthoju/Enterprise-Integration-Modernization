# Architecture

This project uses a Foundry-first architecture for agent operations and governance, while keeping Azure Logic Apps MCP tools as the only path to enterprise systems.

## Platform Roles

| Layer | Responsibility |
|---|---|
| Microsoft Agent Framework | Agent orchestration, intent handling, tool selection, and response composition. |
| Microsoft Foundry | Model hosting, hosted agent operations, tracing, evaluations, safety policy, and release governance. |
| Azure Logic Apps Standard MCP Server | Remote MCP tool surface for approved enterprise workflows. |
| Azure Functions | Validation, transformation, risk scoring, and reusable workflow helpers. |
| Service Bus | Asynchronous integration work, retries, and decoupled backend processing. |
| Application Insights and Log Analytics | Operational telemetry, correlation, alerting, and demo reporting. |

## Request Flow

```text
User / Web UI / VS Code MCP Client
        |
        v
FastAPI Agent API
        |
        v
Microsoft Agent Framework agent shell
        |
        +--> Microsoft Foundry project
        |       +--> model deployment
        |       +--> trace capture
        |       +--> evaluation gates
        |       +--> governance policy checks
        |
        v
Tool registry and risk policy
        |
        v
MCP client adapter
        |
        v
Logic Apps Standard remote MCP server
        |
        v
Approved enterprise workflow
```

## Design Rules

- Foundry is the first-class runtime and governance layer for agent behavior.
- MCP is the mandatory enterprise execution layer for backend actions.
- The agent must not call SAP, ServiceNow, databases, partner APIs, or messaging services directly.
- Risk classification happens before tool execution.
- High-risk tools require approval before execution.
- Every request carries a correlation ID across agent, Foundry trace, MCP call, workflow, and logs.

## Local Mode

Local development uses `MOCK_MCP=true` so the agent can exercise tool selection, risk policy, and response shaping without Azure resources. Mock mode must preserve the same contracts as the remote MCP tools.
