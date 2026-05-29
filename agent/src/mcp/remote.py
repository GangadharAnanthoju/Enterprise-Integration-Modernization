"""Remote MCP transport helpers.

This module keeps the future HTTP transport separate from policy, request
building, and local mock execution. It intentionally does not make network
calls yet.
"""

from dataclasses import dataclass

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

    if not config.endpoint_configured:
        raise RemoteMcpConfigurationError(config.server_name)

    return McpRemoteRequestEnvelope(
        server_name=config.server_name,
        endpoint_url=config.endpoint_url or "",
        tool_name=request.tool_name,
        correlation_id=request.correlation_id,
        payload=request.payload,
        timeout_seconds=config.timeout_seconds,
    )


@dataclass(frozen=True)
class RemoteMcpHttpClient:
    """Placeholder for the future remote MCP HTTP transport."""

    config: McpServerConfig

    def send(self, envelope: McpRemoteRequestEnvelope) -> dict[str, object]:
        """Fail safely until real HTTP transport is implemented."""

        raise RemoteMcpNotImplementedError(envelope.server_name, envelope.endpoint_url)


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
