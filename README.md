# AI-Ready Enterprise Integration Modernization Platform

This project demonstrates a governed enterprise integration modernization pattern using Microsoft Agent Framework, Microsoft Foundry, and Azure Logic Apps Standard as a remote MCP server.

The solution is intentionally built in steps so each platform concern is easy to understand:

1. Repository scaffold
2. Foundry integration baseline
3. FastAPI agent shell
4. MCP client adapter
5. Tool registry and risk policy
6. Mock-mode execution
7. Tests, infrastructure, pipelines, and documentation

## Architecture Direction

- Microsoft Agent Framework orchestrates the agent.
- Microsoft Foundry provides model hosting, runtime operations, evaluations, tracing, and governance.
- Azure Logic Apps Standard exposes enterprise workflows as MCP tools.
- The agent must use MCP tools for enterprise actions instead of directly accessing backend systems.
- High-risk actions require approval before execution.

## Local Development

The project will support local demo mode without Azure by using:

```env
MOCK_MCP=true
```

Implementation starts in `agent/`, with supporting contracts in `docs/`, governance in `foundry/`, mock data in `test-data/`, and Azure deployment templates in `infra/`.
