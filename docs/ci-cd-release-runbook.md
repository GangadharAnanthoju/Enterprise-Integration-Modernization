# CI/CD And Release Runbook

## Purpose

Step 19 turns the proven local deployment scripts into a controlled release
process without hiding the underlying Azure commands.

```text
pull request or push
  -> offline CI validation
  -> manual dev release request
  -> preflight validation
  -> GitHub Environment approval
  -> Azure OIDC login
  -> guarded deployment scripts
  -> APIM smoke test
```

## Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `.github/workflows/ci.yml` | Pull request and push to `dev` or `main` | Lint, tests, release-asset validation, and Docker build |
| `.github/workflows/release-dev.yml` | Manual | Controlled release of all or selected dev components |
| `.github/workflows/rollback-agent.yml` | Manual | Restore an existing immutable agent image tag |

## GitHub Environment Setup

Create a GitHub Environment named `dev`.

Configure required reviewers on that environment. The reviewer approval is the
human release gate before Azure changes begin.

Add or reuse these GitHub repository or `dev` Environment secrets:

```text
AZURE_CLIENT_ID
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
```

They identify the federated deployment identity. Despite being stored as
GitHub secrets, these three identifiers are not credentials by themselves. No
Azure client secret is required because authentication uses OIDC.

## Azure OIDC Setup

Create an Entra application or user-assigned managed identity for GitHub
Actions, then add a federated credential for this repository and the `dev`
GitHub Environment.

Federated subject:

```text
repo:GangadharAnanthoju/Enterprise-Integration-Modernization:environment:dev
```

Grant only the scopes required by the existing deployment scripts:

- project resource group deployment access
- ACR build access
- Container Apps deployment access
- project-specific API access inside shared APIM
- access to update the existing Container App and build immutable ACR images

Shared parent resources must not be deleted by the deployment identity.

Current learning identity:

```text
uami-sysint-github-actions-eastus
resource group: rg-sysint-ideindity-eastus
dev federated subject:
repo:GangadharAnanthoju/Enterprise-Integration-Modernization:environment:dev
```

Normal application releases reuse the Container App managed identity's existing
role assignments and do not require `roleAssignments/write`. Full runtime
provisioning remains a separate privileged operation. If clean runtime
recreation is required, grant a role-assignment-capable role only at the
specific scopes where the Container App managed identity receives access. Do
not grant broad `Owner` solely to make the pipeline convenient.

## CI Validation

Run the same release-asset checks locally:

```powershell
.\infra\scripts\validate-release-assets.ps1
```

The validation checks:

- PowerShell syntax
- required release files
- JSON syntax
- MCP tools mapped to Logic Apps workflows
- Bicep compilation

CI additionally runs Ruff and all offline tests on the same Windows toolchain
used for releases. A separate Linux job validates the production Docker image
build.

## Controlled Release

Preview locally:

```powershell
.\infra\scripts\invoke-release.ps1 `
  -Component all `
  -ImageTag learning-release-01
```

Execute locally after review:

```powershell
.\infra\scripts\invoke-release.ps1 `
  -Component all `
  -ImageTag learning-release-01 `
  -Execute `
  -Confirmation "RELEASE DEV"
```

In GitHub Actions, run **Release Dev**, choose the release scope, and approve
the `dev` Environment gate. If no image tag is supplied, the immutable commit
SHA is used.

Release scopes:

```text
all
logic-apps
agent
apim
smoke-test
```

## Rollback

Every normal release should use an immutable image tag such as the Git commit
SHA. Keep the previous known-good tag before releasing.

Preview:

```powershell
.\infra\scripts\rollback-agent-containerapp.ps1 `
  -ImageTag <known-good-tag>
```

Execute:

```powershell
.\infra\scripts\rollback-agent-containerapp.ps1 `
  -ImageTag <known-good-tag> `
  -Execute `
  -Confirmation "ROLLBACK AGENT"
```

The rollback verifies that the tag exists in ACR, updates only the Container
App image, and requires a successful health check.

## Failure Boundaries

- A failed preflight prevents deployment.
- A rejected GitHub Environment approval prevents Azure login and deployment.
- A failed deployment stops the workflow.
- A failed APIM smoke test marks the release failed.
- Logic Apps MCP key rotation remains an explicit operational checkpoint.
- Runtime deletion remains separate from release automation.

## Release Evidence

For each release, retain:

- workflow run URL
- commit SHA and image tag
- approver
- selected release scope
- smoke-test result
- rollback tag

## Verified Closure Runs

Completed on June 7, 2026:

| Exercise | GitHub Actions run |
|---|---|
| Smoke-test-only controlled release | `27095182678` |
| Immutable agent release | `27095390749` |
| Rollback to `step18g2` | `27095541474` |
| Restore latest immutable image | `27095593489` |

The immutable agent release initially exposed an RBAC design issue: application
releases attempted to recreate managed-identity roles. The release scripts now
reuse existing RBAC assignments, preserving least-privilege GitHub OIDC access.
