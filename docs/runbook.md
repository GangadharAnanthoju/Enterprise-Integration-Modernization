# Runbook

This runbook covers common operational tasks for the Foundry-first, MCP-executed platform.

## Failed MCP Tool Call

1. Capture the `correlation_id` from the user response or API log.
2. Search Application Insights for `mcp.tool.called`.
3. Check the matching Logic Apps workflow run.
4. Confirm whether the failure was authentication, schema validation, backend timeout, or workflow logic.
5. Retest the same tool with the sample request under `logicapps/workflows/<tool>/sample-request.json`.

## Foundry Evaluation Regression

1. Identify the evaluation dataset and failing case.
2. Check whether the failure is tool selection, risk classification, response quality, or unsupported intent handling.
3. Update prompts, policy metadata, or tests before changing runtime code.
4. Record the decision in `foundry/governance/release-checklist.md`.

## Approval Workflow Issue

1. Confirm the tool risk level in `agent/src/tools/registry.py`.
2. Confirm the approval rule in `agent/src/tools/risk_policy.py`.
3. Check `createApprovalRequest` workflow execution.
4. Verify the agent did not execute the high-risk tool before approval.

## Secret Rotation

1. Rotate secrets in Key Vault or the configured identity provider.
2. Update local `.env` only for development environments.
3. Restart affected services.
4. Run the health endpoint and one read-only MCP tool smoke test.

## Dead-Letter or Async Processing Issue

1. Locate the Service Bus message by correlation ID.
2. Review Function App logs for validation or transformation errors.
3. Replay only after confirming idempotency and side-effect safety.
4. Document the incident and preventive fix.
