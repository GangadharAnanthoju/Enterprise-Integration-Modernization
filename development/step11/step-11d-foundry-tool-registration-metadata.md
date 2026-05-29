# Step 11D - Foundry Tool Registration Metadata

## Goal

Prepare Foundry-facing metadata for the approved MCP tools without creating a live Foundry agent yet.

## Added File

```text
agent/src/foundry/tool_registration.py
```

## What This Adds

The new module projects the approved tool registry into registration-ready metadata:

- tool name
- description
- business domain
- backend system
- risk level
- approval requirement
- owner
- required entities
- schema references
- per-tool endpoint environment variable
- execution boundary: MCP
- backend implementation: Logic Apps Standard workflow

## Why This Matters

The approved registry remains the source of truth.

Foundry tool registration should not become a separate hand-maintained list that can drift away from governance policy. This step creates a projection from the governed registry instead.

```text
Tool registry
  -> Foundry tool registration metadata
  -> future Foundry agent tool attachment
```

## Important Boundary

This step does not call Foundry APIs.

It prepares the metadata shape that future registration can use after the Foundry project, model deployment, and registration approach are selected.

## Verification

Tests verify that:

- all approved tools have Foundry-facing metadata
- high-risk tools preserve approval requirements
- endpoint setting names are available for Logic Apps MCP workflow URLs

## Interview Explanation

I did not duplicate the tool catalog for Foundry. I projected the existing approved MCP registry into Foundry-facing registration metadata. That keeps governance centralized while preparing the future Foundry agent to attach the same approved tools.
