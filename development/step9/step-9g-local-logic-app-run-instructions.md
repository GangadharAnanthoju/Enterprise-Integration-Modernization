# Step 9G: Local Logic App Run Instructions

## Goal

Document how to run or prepare the local `getOrderStatus` Logic Apps workflow and connect it to the agent's remote MCP settings.

This step is documentation only because local runtime behavior depends on installed developer tools such as the Logic Apps Standard extension, Azure Functions Core Tools, and Azurite.

## What Changed

- Added local run checklist to `logicapps/standard-app/README.md`.
- Added `logicapps/standard-app/getOrderStatus/local-run.md`.
- Documented the sample request body.
- Documented the expected success and missing-entity responses.
- Documented how the local trigger URL will become `MCP_SERVER_URL`.

## Local Run Flow

```text
Open logicapps/standard-app workspace
  -> Start local Logic Apps runtime
  -> Get local HTTP trigger URL
  -> Send getOrderStatus sample request
  -> Put trigger URL into MCP_SERVER_URL
```

## Agent Remote MCP Flow

```text
/agent/chat
  -> getOrderStatus planned action
  -> McpToolRequest
  -> RemoteMcpHttpClient
  -> local Logic Apps getOrderStatus endpoint
```

## Why This Matters

This is the bridge from local designer work to agent-driven remote execution. Once the local trigger URL is known, we can point the agent's remote MCP client at the local workflow before deploying anything to Azure.

## Interview Talking Point

I tested the integration path in stages: first the workflow design, then local runtime invocation, then the agent's remote MCP client pointing to the local workflow endpoint.
