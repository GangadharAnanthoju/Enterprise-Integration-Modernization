# Step 13A - MAF Foundry Package

## Goal

Install the Foundry SDK support needed to create a real Microsoft Foundry agent from this project.

Step 12 prepared the local MAF shape and preflight checks. Step 13A adds the package dependency that lets the Python code talk to the Foundry project.

## Package Added

```text
agent-framework-foundry
azure-ai-projects
```

These packages support:

- building Foundry-aware agent runtime code
- creating a Foundry project client
- creating or updating Prompt Agent versions in the configured Foundry project

## Why This Is Needed

The local project already has:

- FastAPI as the enterprise control plane
- MCP as the execution boundary
- Logic Apps as backend workflows
- Foundry instructions and registration metadata
- MAF local skeleton

The missing piece was the live Foundry SDK path.

## Important Boundary

This package does not expose Logic Apps directly to the model.

The target design remains:

```text
Foundry Agent
  -> governed MCP tools
  -> FastAPI checks where needed
  -> Logic Apps workflows
```

Step 13A only enables live Foundry registration. Tool attachment and production publishing are later steps.

## Verification

The package was installed into the agent virtual environment:

```text
agent/.venv
```

The dependency list was updated in:

```text
agent/requirements.txt
```
