# Monitoring

Monitoring spans Foundry agent operations and Azure integration telemetry. The goal is to explain what the agent decided, which MCP tool ran, and what happened downstream.

## Telemetry Events

| Event | Producer | Key Fields |
|---|---|---|
| `agent.request.received` | Agent API | `correlation_id`, user/session metadata, timestamp |
| `agent.tool.selected` | Agent Framework layer | `correlation_id`, tool name, intent, confidence if available |
| `agent.risk.evaluated` | Risk policy | `correlation_id`, tool name, risk level, approval required |
| `mcp.tool.called` | MCP adapter | `correlation_id`, tool name, status, latency |
| `workflow.completed` | Logic Apps | `correlation_id`, workflow name, result |
| `foundry.evaluation.completed` | Foundry evaluation | `correlation_id`, dataset, score, pass/fail |

## Correlation

The same `correlation_id` must travel through:

1. FastAPI request
2. Agent Framework run
3. Foundry trace
4. MCP client call
5. Logic Apps workflow
6. Azure Function helper
7. Application Insights and Log Analytics

## Initial Alerts

- MCP tool failure rate above threshold.
- High-risk tool attempted without approval.
- Logic Apps workflow failure.
- Azure Function validation failure spike.
- Foundry evaluation baseline regression.

## Demo Dashboard

The demo should show request count, tool usage by name, approval-required actions, failed workflow runs, and average MCP call latency.
