# Enterprise Integration Logic Apps Standard Project

Open this workspace directly in VS Code when you want to work with the Logic Apps designer:

```text
logicapps/standard-app/Enterprise-Integration-LogicApps.code-workspace
```

This project is separate from the repository root so the designer can recognize the Logic Apps Standard layout without requiring the whole repo to behave like a Logic Apps workspace.

## Open In Designer

1. Open a new VS Code window.
2. Open this workspace file:

   ```text
   C:\Data_AI\projects\Enterprise-Integration-Modernization\logicapps\standard-app\Enterprise-Integration-LogicApps.code-workspace
   ```

3. In that window, open:

   ```text
   getOrderStatus/workflow.json
   ```

4. Right-click the file and select **Open Designer**.

If the extension asks for local settings, copy:

```powershell
Copy-Item local.settings.json.example local.settings.json
```

`local.settings.json` is ignored by git and should not be committed.

For your current Azure setup, the local designer setting is:

```text
WORKFLOWS_RESOURCE_GROUP_NAME=rg-sysint-enterprise-integration-eus
WORKFLOWS_LOCATION_NAME=eastus
```

## Current Workflows

| Workflow | Purpose |
|---|---|
| `checkShipmentStatus` | Read-only shipment status lookup. |
| `createApprovalRequest` | Human approval request creation. |
| `createServiceNowTicket` | Approval-gated ServiceNow ticket creation. |
| `getOrderStatus` | Read-only order status lookup exposed as the first MCP-backed workflow candidate. |
| `queryIntegrationRunStatus` | Read-only integration troubleshooting lookup. |
| `sendSupplierNotification` | Approval-gated supplier notification. |
| `SendEmailNotification` | Enterprise email notification with text or HTML body support. |
| `validateInvoice` | Invoice validation before payment processing. |

## Local Files

| File | Purpose |
|---|---|
| `host.json` | Logic Apps Standard host configuration. |
| `local.settings.json.example` | Local settings template. Copy to `local.settings.json` for local designer/runtime use. |
| `connections.json` | Placeholder connection configuration. |
| `parameters.json` | Placeholder workflow parameters. |
| `Enterprise-Integration-LogicApps.code-workspace` | Workspace file for opening this project separately. |
| `getOrderStatus/workflow.json` | Designer-friendly workflow definition. |
| `getOrderStatus/sample-request.json` | Example request body for local testing. |

Do not commit real secrets in `local.settings.json`.

## Local Runtime Notes

For local execution, the Logic Apps Standard extension may also require:

- Azure Functions Core Tools
- Azurite storage emulator
- A copied `local.settings.json`

Designer inspection can usually happen before the workflow is deployed to Azure. Running the workflow locally may require those runtime tools.

## Local Run Checklist

1. Start Azurite if your local settings use `UseDevelopmentStorage=true`.
2. Press F5 in this workspace and choose `Start local Logic Apps host`.
3. If F5 does not start the host, run the task manually from Command Palette:

   ```text
   Tasks: Run Task -> func: host start
   ```

4. Or open a terminal in:

   ```text
   C:\Data_AI\projects\Enterprise-Integration-Modernization\logicapps\standard-app
   ```

5. Make sure local settings exist:

   ```powershell
   Copy-Item local.settings.json.example local.settings.json
   ```

6. Start the local Logic Apps runtime from the VS Code extension or with Azure Functions Core Tools if available:

   ```powershell
   func start
   ```

7. Use the generated local HTTP trigger URL for `getOrderStatus`.

The sample request body is:

```json
{
  "server_name": "logic-apps-standard-mcp",
  "tool_name": "getOrderStatus",
  "correlation_id": "local-corr-001",
  "payload": {
    "order_id": "ORD-1001"
  },
  "timeout_seconds": 30
}
```

Once the local endpoint is known, it can be used in the agent `.env`:

```env
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
MCP_TOOL_ENDPOINT_GET_ORDER_STATUS=http://localhost:7071/api/<generated-getOrderStatus-route>
MCP_TOOL_ENDPOINT_CHECK_SHIPMENT_STATUS=http://localhost:7071/api/<generated-checkShipmentStatus-route>
MCP_TOOL_ENDPOINT_VALIDATE_INVOICE=http://localhost:7071/api/<generated-validateInvoice-route>
MCP_TOOL_ENDPOINT_QUERY_INTEGRATION_RUN_STATUS=http://localhost:7071/api/<generated-queryIntegrationRunStatus-route>
MCP_TOOL_ENDPOINT_SEND_SUPPLIER_NOTIFICATION=http://localhost:7071/api/<generated-sendSupplierNotification-route>
MCP_TOOL_ENDPOINT_CREATE_SERVICENOW_TICKET=http://localhost:7071/api/<generated-createServiceNowTicket-route>
MCP_TOOL_ENDPOINT_CREATE_APPROVAL_REQUEST=http://localhost:7071/api/<generated-createApprovalRequest-route>
MCP_API_KEY=
```

The exact local URL may vary depending on how the Logic Apps extension starts the workflow runtime.

For local Logic Apps callback URLs, keep `MCP_API_KEY` empty because the URL already includes its own `sig` token.
