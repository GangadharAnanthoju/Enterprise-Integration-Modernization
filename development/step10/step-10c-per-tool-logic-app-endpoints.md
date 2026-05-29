# Step 10C - Per-Tool Logic Apps Endpoint Mapping

## Goal

Treat each Logic Apps workflow as its own MCP tool endpoint.

Step 10B proved the remote MCP HTTP path with `getOrderStatus`. Step 10C changes configuration so the agent can choose a tool and the MCP executor can call that tool's specific Logic Apps callback URL.

## What Changed

- Added per-tool endpoint settings to the agent configuration.
- Kept `MCP_SERVER_URL` as a fallback endpoint.
- Updated remote MCP envelope construction to prefer the selected tool's endpoint.
- Updated environment validation so local Logic Apps callback URLs can work without `MCP_API_KEY`.
- Added tests for per-tool endpoint loading and endpoint selection.

## Endpoint Settings

```env
MCP_TOOL_ENDPOINT_GET_ORDER_STATUS=
MCP_TOOL_ENDPOINT_CHECK_SHIPMENT_STATUS=
MCP_TOOL_ENDPOINT_VALIDATE_INVOICE=
MCP_TOOL_ENDPOINT_QUERY_INTEGRATION_RUN_STATUS=
MCP_TOOL_ENDPOINT_CREATE_APPROVAL_REQUEST=
MCP_TOOL_ENDPOINT_CREATE_SERVICENOW_TICKET=
MCP_TOOL_ENDPOINT_SEND_SUPPLIER_NOTIFICATION=
```

## Routing Behavior

```text
Agent selects getOrderStatus
  -> MCP executor checks MCP_TOOL_ENDPOINT_GET_ORDER_STATUS
  -> if present, calls that URL
  -> otherwise falls back to MCP_SERVER_URL
```

This keeps the project aligned with the architecture goal:

```text
One approved MCP tool = one governed Logic Apps workflow endpoint
```

## Local Authentication Note

For local Logic Apps callback URLs, leave `MCP_API_KEY` empty. The callback URL already includes a `sig` token.

For Azure-hosted endpoints later, `MCP_API_KEY`, APIM subscription keys, managed identity, or OAuth can be added based on the chosen exposure pattern.

## Interview Explanation

Step 10C avoids a temporary dispatcher and keeps the design closer to enterprise MCP tool mapping. The tool registry decides which approved tool is selected, and the MCP runtime maps that tool to its own Logic Apps workflow endpoint. This lets each workflow keep its own contract, risk level, backend mapping, and operational ownership.
