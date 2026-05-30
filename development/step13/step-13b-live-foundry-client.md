# Step 13B - Live Foundry Client

## Goal

Add a small, testable code boundary for creating or updating the real Foundry agent version.

## Code Added

```text
agent/src/foundry/live_agent.py
```

This module contains:

| Function or class | Purpose |
|---|---|
| `create_foundry_project_client` | Creates an `AIProjectClient` using Azure CLI credentials |
| `build_prompt_agent_definition` | Converts the local Foundry instruction file into a Foundry Prompt Agent definition |
| `create_or_update_foundry_prompt_agent_version` | Runs preflight and creates a new Foundry agent version |
| `FoundryAgentVersionResult` | Returns a safe summary of the live operation |
| `FoundryAgentRegistrationError` | Blocks live registration when required settings are missing |

## Environment Inputs

The live client uses values from `agent/.env`:

```text
FOUNDRY_PROJECT_ENDPOINT
MODEL_DEPLOYMENT_NAME
FOUNDRY_AGENT_NAME
```

It authenticates with:

```text
AzureCliCredential
```

That means the developer must already be signed in with Azure CLI and have permission on the Foundry project.

## Preflight Gate

Before making a live Foundry call, the code runs:

```text
run_foundry_registration_preflight
```

This prevents accidental cloud writes when required values are missing or the local agent definition is not ready.

## Why This Code Is Isolated

Foundry SDKs and hosted-agent patterns can change over time. Keeping live registration in one module protects the rest of the project:

- FastAPI routes stay stable
- MCP execution stays stable
- Logic Apps endpoints stay stable
- approval and audit behavior stay stable

The only part that needs SDK-specific changes is the Foundry adapter boundary.

## Tests Added

```text
agent/tests/test_foundry_live_agent.py
```

The tests use fake Foundry clients, so normal unit tests do not create cloud resources.
