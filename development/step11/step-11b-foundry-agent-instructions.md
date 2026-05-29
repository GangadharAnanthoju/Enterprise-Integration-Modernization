# Step 11B - Foundry Agent Instructions

## Goal

Create the instruction file for the future Foundry-hosted enterprise integration agent.

This step defines how the agent should behave before we create a real Foundry agent resource or register tools.

## Added File

```text
agent/src/prompts/foundry_agent_instructions.md
```

## What The Instructions Cover

- Agent role and scope
- Approved tool-only behavior
- Missing entity behavior
- High-risk approval rules
- Response style
- MCP execution envelope
- Failure behavior
- Foundry governance alignment

## Why This Comes Before Tool Registration

Tool registration tells Foundry what tools are available.

Agent instructions tell Foundry how the agent should reason about those tools.

For this project, the safety behavior is as important as the tool list:

```text
User request
  -> agent follows instructions
  -> selects approved tool
  -> checks entities
  -> respects risk policy
  -> uses MCP execution
```

## Key Instruction Themes

1. Do not invent tools.
2. Do not bypass MCP.
3. Ask for missing required entities.
4. Do not execute high-risk actions without approval.
5. Preserve correlation IDs.
6. Keep responses auditable and operationally useful.

## Interview Explanation

Before creating the Foundry agent, I wrote the agent's operating instructions. These instructions define the safety contract: use only approved tools, ask for missing entities, preserve correlation IDs, and require approval for high-risk actions. This makes the eventual Foundry agent behavior explicit and testable.
