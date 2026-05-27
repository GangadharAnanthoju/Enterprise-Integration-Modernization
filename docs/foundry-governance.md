# Foundry Governance

Microsoft Foundry is the governance center for this project. It owns model selection records, agent run traceability, evaluation gates, safety policy alignment, and release readiness.

## Governance Scope

| Area | Foundry-First Requirement |
|---|---|
| Model selection | Record the selected model, deployment name, region, SKU, fallback plan, and reason for selection. |
| Agent runtime | Keep hosted agent and `AIProjectClient` integration isolated under `agent/src/foundry/` and `agent/src/agent_app.py`. |
| Evaluations | Run baseline evaluation datasets before release and after policy/tool changes. |
| Tracing | Capture agent inputs, selected tools, risk decisions, MCP call outcomes, and correlation IDs. |
| Safety | Align responses and tool use with the safety policies in `foundry/governance/safety-policies.md`. |
| Release checks | Complete `foundry/governance/release-checklist.md` before demo or deployment milestones. |

## Evaluation Gates

Minimum gates for this portfolio project:

1. The agent selects the expected MCP tool for common enterprise requests.
2. The agent refuses or escalates unsupported enterprise actions.
3. High-risk tools trigger approval instead of immediate execution.
4. Tool responses include enough operational context for troubleshooting.
5. No response claims that backend work happened unless the MCP tool result confirms it.

## Trace Requirements

Every agent run should include:

- `correlation_id`
- user intent summary
- selected tool name
- risk level
- approval decision when required
- MCP request and response status
- Foundry evaluation result when part of a test run

## Version Freshness

Microsoft Agent Framework and Foundry SDK capabilities change quickly. Before each sprint, verify current package names, supported hosted agent patterns, and evaluation APIs. Record decisions in `foundry/governance/release-checklist.md`.
