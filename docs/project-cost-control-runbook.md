# Enterprise Integration Modernization - Cost Control Runbook

## Purpose

Safely reduce Azure cost when the learning environment is idle, then recreate
the full governed Foundry-to-MCP architecture without deleting shared platform
resources.

## Ownership Boundary

### Project-Owned Resources

These resources belong to this project:

| Resource | Name | Cost Note |
|---|---|---|
| Logic App Standard | `la-sysint-enterprise-integration-eus` | Runs on the WS1 plan |
| Workflow Standard plan | `asp-sysint-enterprise-integration-eus` | Primary idle-cost target |
| Storage account | `stsysintintegeus001` | Stores Logic Apps state, audit, and approvals |
| Container App | `ca-sysint-enterprise-agent-eus` | Consumption-based, configured to scale to zero |

### Shared Resources

Never delete these from this project:

- `aca-env-sysint-eus`
- `acrsysintcommoneus`
- `kv-sysint-common-eus`
- `apim-sysint-common-eus`
- `appi-sysint-common-dev-eus`
- `log-sysint-common-eus`
- `ms-foundry-sysint-02/proj-sysint-01`

Project-specific APIM API/product/subscription and ACR images may be cleaned up,
but the shared parent services must remain.

## Cost Facts

### Logic Apps WS1

Stopping the Logic App does not remove the Workflow Standard plan charge.
Delete the Logic App and WS1 plan when real idle-cost reduction is required.

### Container App

The Container App uses:

```text
minReplicas: 0
maxReplicas: 2
```

It can scale to zero when idle. Delete it only when you want a fully clean
project runtime or want to prove recreation.

### Storage

Keeping storage preserves:

- Logic Apps state
- `AgentAuditEvents`
- `AgentApprovalRequests`
- `AgentApprovalDecisions`

Deleting storage loses those durable records. Storage is therefore retained by
default during cleanup.

### Shared Consumption APIM

The shared APIM Consumption service does not have this project's dedicated idle
instance charge. Keeping the project API artifacts is acceptable, but remove
them when testing a fully clean recreation.

## Read-Only Cost Posture

```powershell
.\infra\scripts\show-project-cost-posture.ps1
```

This inventories project-owned resources, Container App scaling, and
project-specific APIM artifacts. It changes nothing.

## Recommended Idle Cleanup

## Current Idle State

On June 7, 2026, the project entered a partial idle state:

- Logic App Standard app: deleted
- dedicated WS1 plan: deleted
- Container App/UI: retained with `minReplicas=0`
- storage and durable records: retained
- APIM artifacts: retained
- shared platform services: retained

Because the Container App remains configured for remote MCP mode, tool
execution fails until Logic Apps is recreated. This is intentional; there is no
automatic mock fallback.

For the exact current-state handoff, see:

```text
docs/current-runtime-state.md
```

## Full Runtime Idle Cleanup

Plan only:

```powershell
.\infra\scripts\remove-project-runtime.ps1
```

Execute while keeping storage and APIM artifacts:

```powershell
.\infra\scripts\remove-project-runtime.ps1 `
  -Execute `
  -Confirmation "DELETE PROJECT RUNTIME"
```

This deletes:

- Container App
- Container App managed identity role assignments
- Logic App Standard app
- WS1 Workflow Standard plan

This keeps:

- project storage and durable audit/approval data
- project APIM artifacts
- all shared platform resources

## Full Project Runtime Cleanup

To also remove project APIM artifacts:

```powershell
.\infra\scripts\remove-project-runtime.ps1 `
  -DeleteApimArtifacts `
  -Execute `
  -Confirmation "DELETE PROJECT RUNTIME"
```

To also delete project storage and durable records:

```powershell
.\infra\scripts\remove-project-runtime.ps1 `
  -DeleteStorage `
  -DeleteApimArtifacts `
  -Execute `
  -Confirmation "DELETE PROJECT RUNTIME"
```

Use `-DeleteStorage` only when data loss is intentional.

The cleanup script is idempotent: it checks whether each project resource or
APIM artifact exists before attempting removal.

## Recreate

Plan only:

```powershell
.\infra\scripts\recreate-project-runtime.ps1
```

Execute:

```powershell
.\infra\scripts\recreate-project-runtime.ps1 `
  -ContainerImageTag recreated-01 `
  -Execute
```

Recreation order:

1. Deploy Logic Apps infrastructure from Bicep.
2. Publish workflows and managed MCP server metadata.
3. Confirm the Logic Apps MCP API key is current in Key Vault.
4. Deploy the FastAPI Container App and managed-identity roles.
5. Deploy APIM API, policy, product, and subscription.
6. Run the APIM end-to-end test.

The script pauses at the MCP API key checkpoint because deleting and recreating
the Logic App can require regenerating its key.

## Verify

```powershell
.\infra\scripts\test-agent-apim.ps1
```

Expected:

```text
no_key_status: 401
health: ok
chat_status: completed
selected_tool: getOrderStatus
execution_mode: remote
tool_status: completed
```

## Suggested Learning Routine

```text
deploy -> verify -> learn/demo -> capture notes -> clean up WS1 runtime
```

This keeps the project reproducible while avoiding unnecessary idle compute
charges.
