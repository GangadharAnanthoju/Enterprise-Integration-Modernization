# Step 5E: Foundry Agent Adapter Boundary

## Goal

Add a stable agent runtime adapter so FastAPI no longer depends directly on the temporary rule-based chat function.

This keeps Microsoft Foundry first-class in the architecture: the API can call a generic agent runtime adapter today, and a future Foundry / Microsoft Agent Framework implementation can replace the local rule-based shell later.

## What Changed

- Added `foundry.agent_adapter.AgentRuntimeAdapter`.
- Added `LocalRuleBasedAgentAdapter` as the current temporary implementation.
- Added `get_agent_adapter()` as the factory FastAPI uses to get the active runtime.
- Updated `/agent/chat` to call the adapter instead of calling `handle_chat_message()` directly.
- Added `/foundry/agent-adapter` so developers can see the active runtime boundary.

## Current Flow

1. FastAPI receives `/agent/chat`.
2. The API resolves a correlation ID.
3. The API asks `get_agent_adapter()` for the active runtime.
4. The adapter handles chat planning or governed simulation.
5. Today, the adapter delegates to the local rule-based shell.
6. Later, the adapter can delegate to a Foundry-hosted agent.

## Why This Matters

Without this boundary, API routes would be tightly coupled to temporary learning code. With the adapter boundary, the project can mature from local mock behavior to real Foundry runtime behavior without changing the public chat API.

## Interview Talking Point

The important design choice is that the API depends on an agent runtime interface, not a specific agent implementation. That makes the modernization path realistic: start with a transparent local planner, then swap in Microsoft Foundry / Agent Framework when the runtime is ready.
