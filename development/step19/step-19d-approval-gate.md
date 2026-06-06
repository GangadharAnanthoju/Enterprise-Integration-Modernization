# Step 19D - Release Approval Gate

The release and rollback workflows use the GitHub Environment named `dev`.

Required reviewers on that Environment provide the human approval gate. Azure
authentication uses OIDC and does not require a stored client secret.
