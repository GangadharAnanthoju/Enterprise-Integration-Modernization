# Step 12C - MAF And Foundry Registration Plan

## Goal

Prepare the registration plan for a Microsoft Agent Framework agent running in Microsoft Foundry.

This step does not create the live Foundry agent. It creates the local registration contract and preflight validation.

## Added Files

```text
agent/src/foundry/registration_plan.py
agent/tests/test_foundry_registration_plan.py
foundry/governance/maf-foundry-registration-plan.md
development/step12/step-12c-maf-foundry-registration-plan.md
```

## Updated File

```text
foundry/agent-definitions/enterprise-integration-agent.yaml
```

The agent definition now explicitly declares:

```yaml
framework: microsoft_agent_framework
targetImplementation: maf_foundry_agent_adapter
```

## What The Preflight Checks

- `FOUNDRY_PROJECT_ENDPOINT`
- `MODEL_DEPLOYMENT_NAME`
- `FOUNDRY_AGENT_NAME`
- agent name alignment with the local definition
- instruction file availability
- Microsoft Agent Framework declaration
- approved tool registration metadata

## Registration Versus Publishing

Registration creates or updates the agent inside the Foundry project.

Publishing promotes a tested agent version into an Agent Application with a stable endpoint and RBAC-controlled invocation.

For this project:

```text
Register first
  -> test
  -> evaluate
  -> attach/validate tools
  -> publish later
```

## Interview Explanation

I separated registration from publishing. Registration creates the MAF-backed Foundry agent inside the project using the instruction file and model deployment. Publishing comes later after testing and evaluations, when the agent is ready to become an Agent Application for external consumers.
