# Parking List

Items intentionally paused so they remain visible without blocking the current
learning path.

## Completed Release Pipeline Verification

- `Release Dev` with `component: smoke-test` passed
- GitHub `dev` Environment job and Azure OIDC login passed
- immutable commit-SHA image release passed
- post-release APIM smoke test passed
- approved rollback to `step18g2` passed
- restore to the latest immutable image passed

Normal application releases now reuse existing managed-identity RBAC. Explicit
runtime provisioning remains responsible for creating role assignments.

## Intentionally Deferred

- full runtime deletion and recreation
- Microsoft Entra browser authentication
- private networking and additional target-architecture services
