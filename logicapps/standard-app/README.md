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
| `getOrderStatus` | Read-only order status lookup exposed as the first MCP-backed workflow candidate. |

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
