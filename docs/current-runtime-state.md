# Current Runtime State

Last verified: June 7, 2026

## Purpose

This is the first document to read when resuming the project in a new chat or
development session.

## Final State

The project implementation, production validation, CI/CD exercises, and
documentation are complete. The Azure Logic Apps Standard runtime was
intentionally deleted after validation to stop the dedicated WS1 plan charge.

## Currently Running

| Component | State |
|---|---|
| Operational UI and API Container App | Running |
| Container App health endpoint | `ok` |
| Operational UI | HTTP 200 |
| Azure Table Storage | Retained |
| Project APIM API, product, and subscription | Retained |
| Foundry project and agent | Retained shared platform resource |
| Key Vault, ACR, Application Insights, Log Analytics | Retained shared platform resources |

Operational UI:

```text
https://ca-sysint-enterprise-agent-eus.kindmushroom-93329cd8.eastus.azurecontainerapps.io/ui/
```

## Intentionally Deleted

```text
la-sysint-enterprise-integration-eus
asp-sysint-enterprise-integration-eus
```

The deleted resources were the Logic Apps Standard app and its dedicated WS1
plan. This removes the primary project-specific idle compute charge.

## Expected Behavior

The deployed Container App remains configured for remote MCP execution:

```text
MOCK_MCP=false
MCP_EXECUTION_MODE=remote
```

Therefore:

- UI and health endpoints continue working.
- Planning and non-execution API behavior may continue working.
- MCP tool execution fails while the Logic App MCP server is absent.
- The application does not silently return mock results.
- The last verified post-deletion remote execution returned HTTP 500, as expected.

## Recreate Logic Apps When Needed

From the repository root:

```powershell
.\infra\scripts\deploy-dev.ps1
.\infra\scripts\publish-logicapps.ps1
```

After recreation:

1. Verify the managed MCP server and eight tools.
2. Refresh the MCP API key in Key Vault if recreation generated a new key.
3. Restart or redeploy the Container App if required.
4. Run:

```powershell
.\infra\scripts\test-agent-apim.ps1
```

Expected successful execution returns `execution_mode: remote`.

## Closure References

- `docs/project-closure-report.md`
- `docs/architecture.md`
- `docs/demo-script.md`
- `docs/ci-cd-release-runbook.md`
- `docs/project-cost-control-runbook.md`
- `development/project-status-roadmap.md`

