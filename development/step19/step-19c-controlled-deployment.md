# Step 19C - Controlled Deployment

Added `invoke-release.ps1` and the manual `Release Dev` GitHub Actions workflow.

The workflow supports complete and component-scoped releases while preserving
the established deployment sequence:

```text
Logic Apps -> agent -> APIM -> smoke test
```
