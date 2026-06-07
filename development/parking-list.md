# Parking List

Items intentionally paused so they remain visible without blocking the current
learning path.

## Release Pipeline Live Verification

- run `Release Dev` with `component: smoke-test`
- verify GitHub `dev` Environment reviewer approval
- verify GitHub OIDC Azure login
- release an immutable agent image tag through the workflow
- run the post-release APIM smoke test
- test the manually approved rollback workflow
- grant narrowly scoped role-assignment permissions before testing full runtime recreation

The CI workflow itself is active and passing. These are live Azure release
exercises to complete after the UI work.
