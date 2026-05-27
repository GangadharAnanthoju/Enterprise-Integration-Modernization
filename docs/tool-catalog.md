# Tool Catalog

The tool catalog defines the approved MCP tools exposed through Azure Logic Apps Standard. These tools are the only supported path from the agent to enterprise systems.

| Tool | Purpose | Risk | Approval | Backend Pattern |
|---|---|---:|---|---|
| `getOrderStatus` | Look up order status and fulfillment state. | Low | No | Read-only workflow with mock order data. |
| `validateInvoice` | Validate invoice fields and business rules. | Medium | No | Validation workflow plus Azure Function helper. |
| `checkShipmentStatus` | Retrieve shipment status and delivery exceptions. | Low | No | Read-only workflow with mock shipment data. |
| `sendSupplierNotification` | Send a supplier-facing notification. | High | Yes | Approval gate, then outbound workflow. |
| `createApprovalRequest` | Create a human approval task. | Medium | No | Approval workflow simulation. |
| `createServiceNowTicket` | Open an operational support ticket. | High | Yes | Approval gate, then ticket workflow. |
| `queryIntegrationRunStatus` | Troubleshoot integration run status by correlation ID. | Low | No | Read-only operational lookup. |

## Catalog Rules

- Each tool must have a schema, sample request, sample response, owner, risk level, and approval rule.
- Tool names in code, docs, Logic Apps folders, and Foundry policy files must match exactly.
- The agent can discover metadata locally, but execution must go through MCP or mock MCP mode.
- High-risk tools must return an approval-required response until approval is granted.

## Documentation Sources

- Code metadata: `agent/src/tools/registry.py`
- Tool contracts: `agent/src/tools/contracts.py`
- Runtime policy: `agent/src/tools/risk_policy.py`
- Foundry access policy: `foundry/agent-definitions/tool-access-policy.yaml`
- Logic Apps samples: `logicapps/workflows/*/sample-request.json`
