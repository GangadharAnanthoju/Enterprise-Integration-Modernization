"""Remote MCP transport helpers."""

from dataclasses import dataclass

import httpx

from mcp.exceptions import (
    RemoteMcpAuthenticationError,
    RemoteMcpBackendError,
    RemoteMcpConfigurationError,
    RemoteMcpNotImplementedError,
    RemoteMcpTimeoutError,
)
from mcp.schemas import McpRemoteRequestEnvelope, McpServerConfig, McpToolRequest


def build_remote_request_envelope(
    config: McpServerConfig,
    request: McpToolRequest,
) -> McpRemoteRequestEnvelope:
    """Build the HTTP-ready envelope for a future remote MCP request."""

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
        """POST the MCP envelope to the configured remote endpoint."""

        headers = {
            "Content-Type": "application/json",
            "X-Correlation-ID": envelope.correlation_id,
            "X-MCP-Tool-Name": envelope.tool_name,
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        try:
            with httpx.Client(
                timeout=envelope.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = client.post(
                    envelope.endpoint_url,
                    json=envelope.to_http_json(),
                    headers=headers,
                )
        except httpx.TimeoutException as exc:
            raise RemoteMcpTimeoutError(
                envelope.server_name,
                envelope.timeout_seconds,
            ) from exc

        if response.status_code >= 400:
            raise map_remote_http_error(
                server_name=envelope.server_name,
                status_code=response.status_code,
                detail=response.text,
                timeout_seconds=envelope.timeout_seconds,
            )

        try:
            body = response.json()
        except ValueError as exc:
            raise RemoteMcpBackendError(
                envelope.server_name,
                response.status_code,
                "Remote MCP response was not valid JSON.",
            ) from exc

        if not isinstance(body, dict):
            raise RemoteMcpBackendError(
                envelope.server_name,
                response.status_code,
                "Remote MCP response JSON must be an object.",
            )

        return body


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
