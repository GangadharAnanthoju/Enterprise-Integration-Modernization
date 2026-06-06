# Step 19E - Post-Deployment Smoke Tests

The complete release finishes with the existing APIM end-to-end test.

The smoke test verifies:

- APIM rejects requests without a subscription key
- health endpoint succeeds with a subscription
- agent chat completes
- the expected MCP tool executes remotely
