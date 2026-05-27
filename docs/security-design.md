# Security Design

Security is designed around least privilege, managed identity, and governed tool execution. Foundry governs agent behavior; MCP governs enterprise actions.

## Control Model

| Control | Project Direction |
|---|---|
| Identity | Use Microsoft Entra ID for human and service authentication. |
| Agent access | Restrict Foundry project access by role and environment. |
| MCP access | Protect Logic Apps MCP endpoints with Easy Auth or equivalent authenticated access. |
| Secrets | Store production secrets in Key Vault; keep local values in `.env` only for development. |
| Backend access | Use managed identity from Logic Apps and Functions where possible. |
| Authorization | Enforce tool-level risk policy before execution. |
| Approval | Require human approval for high-risk enterprise actions. |
| Audit | Log correlation ID, identity, tool name, risk level, approval status, and outcome. |

## Non-Negotiable Rules

- The agent must not directly call enterprise systems.
- The agent must not embed credentials in prompts, traces, or responses.
- Tool outputs should be summarized for the user without exposing sensitive backend details.
- High-risk tools must pause for approval before side effects occur.
- Foundry traces and operational logs must use the same correlation ID.

## Local Development

Use `.env.example` as the source of local configuration names. Local mock mode may use sample data, but it should preserve production-style authorization and risk decisions.
