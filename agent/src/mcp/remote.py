"""Remote MCP transport helpers."""

from dataclasses import dataclass
import json
from typing import Any

import httpx

from mcp.exceptions import (
    RemoteMcpAuthenticationError,
    RemoteMcpBackendError,
    RemoteMcpConfigurationError,
    RemoteMcpTimeoutError,
)
from mcp.schemas import McpRemoteRequestEnvelope, McpServerConfig, McpToolRequest

MCP_PROTOCOL_VERSION = "2025-06-18"


def build_remote_request_envelope(
    config: McpServerConfig,
    request: McpToolRequest,
) -> McpRemoteRequestEnvelope:
    """Build the HTTP-ready envelope for a remote MCP request."""

    endpoint_url = config.endpoint_for_tool(request.tool_name)
    if not endpoint_url:
        raise RemoteMcpConfigurationError(config.server_name)

    return McpRemoteRequestEnvelope(
        server_name=config.server_name,
        endpoint_url=endpoint_url,
        tool_name=request.tool_name,
        correlation_id=request.correlation_id,
        payload=request.payload,
        timeout_seconds=config.timeout_seconds,
    )


@dataclass(frozen=True)
class RemoteMcpHttpClient:
    """HTTP client for remote Logic Apps Standard MCP execution."""

    config: McpServerConfig
    transport: httpx.BaseTransport | None = None

    def send(self, envelope: McpRemoteRequestEnvelope) -> dict[str, object]:
        """Call one tool through the managed MCP Streamable HTTP endpoint."""

        try:
            with httpx.Client(
                timeout=envelope.timeout_seconds,
                transport=self.transport,
            ) as client:
                initialize_response = self._post_json_rpc(
                    client=client,
                    envelope=envelope,
                    body=_initialize_request(envelope.correlation_id),
                )
                negotiated_version = _protocol_version_from_initialize(
                    initialize_response,
                )
                session_id = initialize_response.headers.get("Mcp-Session-Id")

                self._post_json_rpc_notification(
                    client=client,
                    envelope=envelope,
                    body={"jsonrpc": "2.0", "method": "notifications/initialized"},
                    protocol_version=negotiated_version,
                    session_id=session_id,
                )

                tool_response = self._post_json_rpc(
                    client=client,
                    envelope=envelope,
                    body=_tool_call_request(envelope),
                    protocol_version=negotiated_version,
                    session_id=session_id,
                )
        except httpx.TimeoutException as exc:
            raise RemoteMcpTimeoutError(
                envelope.server_name,
                envelope.timeout_seconds,
            ) from exc
        except httpx.HTTPError as exc:
            raise RemoteMcpBackendError(
                envelope.server_name,
                0,
                str(exc),
            ) from exc

        rpc_response = _parse_json_rpc_response(envelope, tool_response)
        tool_result = rpc_response.get("result")
        if not isinstance(tool_result, dict):
            raise RemoteMcpBackendError(
                envelope.server_name,
                tool_response.status_code,
                "Remote MCP tools/call response did not include a result object.",
            )

        if tool_result.get("isError") is True:
            raise RemoteMcpBackendError(
                envelope.server_name,
                tool_response.status_code,
                _content_text(tool_result) or "Remote MCP tool returned an error.",
            )

        workflow_result = _normalize_tool_result(tool_result)
        if isinstance(workflow_result, dict) and "status" in workflow_result:
            return workflow_result

        return {
            "status": "completed",
            "result": workflow_result if isinstance(workflow_result, dict) else None,
            "message": "Remote MCP execution completed.",
        }

    def _post_json_rpc(
        self,
        *,
        client: httpx.Client,
        envelope: McpRemoteRequestEnvelope,
        body: dict[str, Any],
        protocol_version: str | None = None,
        session_id: str | None = None,
    ) -> httpx.Response:
        """POST one JSON-RPC request and require an MCP response."""

        response = client.post(
            envelope.endpoint_url,
            json=body,
            headers=_headers(
                config=self.config,
                envelope=envelope,
                protocol_version=protocol_version,
                session_id=session_id,
            ),
        )
        _raise_for_remote_error(envelope, response)
        return response

    def _post_json_rpc_notification(
        self,
        *,
        client: httpx.Client,
        envelope: McpRemoteRequestEnvelope,
        body: dict[str, Any],
        protocol_version: str,
        session_id: str | None,
    ) -> None:
        """POST one JSON-RPC notification and accept empty 202 responses."""

        response = client.post(
            envelope.endpoint_url,
            json=body,
            headers=_headers(
                config=self.config,
                envelope=envelope,
                protocol_version=protocol_version,
                session_id=session_id,
            ),
        )
        _raise_for_remote_error(envelope, response)


def _headers(
    *,
    config: McpServerConfig,
    envelope: McpRemoteRequestEnvelope,
    protocol_version: str | None = None,
    session_id: str | None = None,
) -> dict[str, str]:
    """Build MCP Streamable HTTP headers without exposing secrets."""

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "X-Correlation-ID": envelope.correlation_id,
    }
    if config.api_key:
        headers["X-API-Key"] = config.api_key
    if protocol_version:
        headers["MCP-Protocol-Version"] = protocol_version
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    return headers


def _initialize_request(correlation_id: str) -> dict[str, Any]:
    """Return the MCP initialize request."""

    return {
        "jsonrpc": "2.0",
        "id": f"{correlation_id}-initialize",
        "method": "initialize",
        "params": {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {
                "name": "enterprise-integration-modernization-agent",
                "version": "0.1.0",
            },
        },
    }


def _tool_call_request(envelope: McpRemoteRequestEnvelope) -> dict[str, Any]:
    """Return the MCP tools/call request for one governed tool."""

    return {
        "jsonrpc": "2.0",
        "id": f"{envelope.correlation_id}-tool-call",
        "method": "tools/call",
        "params": {
            "name": envelope.tool_name,
            "arguments": envelope.to_http_json(),
        },
    }


def _protocol_version_from_initialize(response: httpx.Response) -> str:
    """Return negotiated MCP protocol version or the version we requested."""

    body = _parse_response_body(response)
    result = body.get("result") if isinstance(body, dict) else None
    if isinstance(result, dict) and isinstance(result.get("protocolVersion"), str):
        return result["protocolVersion"]

    return MCP_PROTOCOL_VERSION


def _parse_json_rpc_response(
    envelope: McpRemoteRequestEnvelope,
    response: httpx.Response,
) -> dict[str, Any]:
    """Parse and validate a JSON-RPC response from JSON or SSE content."""

    body = _parse_response_body(response)
    if not isinstance(body, dict):
        raise RemoteMcpBackendError(
            envelope.server_name,
            response.status_code,
            "Remote MCP response JSON must be an object.",
        )

    if "error" in body:
        raise RemoteMcpBackendError(
            envelope.server_name,
            response.status_code,
            json.dumps(body["error"], separators=(",", ":")),
        )

    return body


def _parse_response_body(response: httpx.Response) -> dict[str, Any]:
    """Parse application/json or text/event-stream MCP response bodies."""

    content_type = response.headers.get("content-type", "")
    if "text/event-stream" in content_type:
        return _parse_sse_json(response.text)

    try:
        body = response.json()
    except ValueError as exc:
        raise RemoteMcpBackendError(
            "remote-mcp",
            response.status_code,
            "Remote MCP response was not valid JSON.",
        ) from exc

    if not isinstance(body, dict):
        raise RemoteMcpBackendError(
            "remote-mcp",
            response.status_code,
            "Remote MCP response JSON must be an object.",
        )

    return body


def _parse_sse_json(text: str) -> dict[str, Any]:
    """Return the first JSON object carried by an SSE data event."""

    for line in text.splitlines():
        if not line.startswith("data:"):
            continue
        payload = line.removeprefix("data:").strip()
        if not payload or payload == "[DONE]":
            continue
        parsed = json.loads(payload)
        if isinstance(parsed, dict):
            return parsed

    raise RemoteMcpBackendError(
        "remote-mcp",
        200,
        "Remote MCP SSE response did not include a JSON data event.",
    )


def _normalize_tool_result(tool_result: dict[str, Any]) -> dict[str, Any] | None:
    """Convert MCP tool result content into the workflow response shape."""

    structured_content = tool_result.get("structuredContent")
    if isinstance(structured_content, dict):
        return structured_content

    text = _content_text(tool_result)
    if not text:
        return None

    try:
        parsed_text = json.loads(text)
    except ValueError:
        return {"content": text}

    return parsed_text if isinstance(parsed_text, dict) else {"content": text}


def _content_text(tool_result: dict[str, Any]) -> str | None:
    """Return concatenated text content from an MCP tool result."""

    content = tool_result.get("content")
    if not isinstance(content, list):
        return None

    text_parts = [
        item.get("text")
        for item in content
        if isinstance(item, dict)
        and item.get("type") == "text"
        and isinstance(item.get("text"), str)
    ]
    return "\n".join(text_parts) if text_parts else None


def _raise_for_remote_error(
    envelope: McpRemoteRequestEnvelope,
    response: httpx.Response,
) -> None:
    """Map HTTP errors into explicit MCP exceptions."""

    if response.status_code >= 400:
        raise map_remote_http_error(
            server_name=envelope.server_name,
            status_code=response.status_code,
            detail=response.text,
            timeout_seconds=envelope.timeout_seconds,
        )


def map_remote_http_error(
    *,
    server_name: str,
    status_code: int,
    detail: str,
    timeout_seconds: int,
) -> RemoteMcpAuthenticationError | RemoteMcpBackendError | RemoteMcpTimeoutError:
    """Map remote HTTP-style failures into explicit MCP exceptions."""

    if status_code in {401, 403}:
        return RemoteMcpAuthenticationError(server_name, status_code)

    if status_code == 408 or status_code == 504:
        return RemoteMcpTimeoutError(server_name, timeout_seconds)

    return RemoteMcpBackendError(server_name, status_code, detail)
