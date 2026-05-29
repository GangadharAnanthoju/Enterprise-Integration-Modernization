# Step 12D - Local MAF Agent Skeleton

## Goal

Add the first local Microsoft Agent Framework-shaped agent skeleton without calling Foundry yet.

This step prepares the code shape that will later replace the temporary rule-based agent adapter.

## Added Files

```text
agent/src/maf_runtime/__init__.py
agent/src/maf_runtime/enterprise_agent.py
agent/tests/test_maf_agent_skeleton.py
```

## Updated Files

```text
agent/src/foundry/agent_adapter.py
agent/src/foundry/governance.py
agent/tests/test_agent_flow.py
agent/tests/test_foundry_governance.py
```

## What The Skeleton Does

The MAF skeleton loads:

- `FOUNDRY_AGENT_NAME`
- `FOUNDRY_PROJECT_ENDPOINT`
- `MODEL_DEPLOYMENT_NAME`
- `agent/src/prompts/foundry_agent_instructions.md`

It also records the intended runtime shape:

```text
framework: microsoft_agent_framework
provider: agent_framework.foundry
tool execution boundary: MCP
enterprise control plane: FastAPI
```

## What It Does Not Do Yet

- It does not invoke a live Foundry agent.
- It does not publish an Agent Application.
- It does not attach tools inside Foundry.
- It does not bypass FastAPI governance.

## Why The MAF Package Is Not Required Yet

The skeleton checks package availability as informational metadata, but tests do not require the package.

This keeps the project stable while we finish the architecture and registration path. The live MAF dependency should be installed when we implement actual Foundry invocation.

## Interview Explanation

I added a local Microsoft Agent Framework-shaped skeleton before switching runtime behavior. It loads the same instructions and Foundry runtime settings that the real agent will need, but keeps execution behind the existing FastAPI and MCP governance path until live Foundry invocation is implemented.
