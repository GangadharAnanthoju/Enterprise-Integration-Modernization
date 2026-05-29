# Step 12E - Foundry Invocation Boundary Plan

## Goal

Define how the project will move from local MAF skeleton to live Foundry invocation.

## Target Flow

```text
Chatbot UI
  -> FastAPI /agent/chat
    -> MAF Foundry adapter
      -> Foundry project agent
        -> approved MCP tool layer
          -> Logic Apps workflows
```

## Runtime Boundary

FastAPI remains the enterprise control plane.

The MAF adapter should be responsible for:

- sending the user message to the Foundry agent
- passing correlation context
- receiving the model/agent response
- returning structured output compatible with the existing API

FastAPI and the backend governance code remain responsible for:

- approved tool catalog enforcement
- required entity validation
- risk policy
- approval checks
- MCP request building
- audit events
- readiness and diagnostics

## Registration Before Publishing

The next live Foundry sequence should be:

```text
Create/register agent in Foundry project
  -> invoke/test inside project
  -> attach/validate MCP tool layer
  -> run evaluations
  -> publish later as Agent Application
```

Publishing is not part of Step 12.

## Interview Explanation

I kept invocation separate from publishing. The first goal is to make the MAF adapter invoke an agent inside the Foundry project while FastAPI still enforces enterprise governance. Publishing as an Agent Application should happen only after registration, invocation, tools, and evaluations are stable.
