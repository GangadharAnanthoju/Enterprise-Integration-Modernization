"""MCP request and response schemas."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


@dataclass(frozen=True)
class McpToolRequest:
    """Request payload prepared for one approved MCP tool call."""

    tool_name: str
    correlation_id: str
    payload: dict[str, Any]


class McpExecutionMode(StrEnum):
    """Supported MCP execution modes."""

    MOCK = "mock"
    REMOTE = "remote"


@dataclass(frozen=True)
class McpServerConfig:
    """Runtime configuration for the enterprise MCP execution boundary."""

    mode: McpExecutionMode
    server_name: str
    endpoint_url: str | None
    timeout_seconds: int
    api_key: str | None = None
    tool_endpoints: dict[str, str] | None = None

    @property
    def endpoint_configured(self) -> bool:
        """Return whether any remote MCP endpoint URL is configured."""

        return bool(self.endpoint_url or self.tool_endpoints)

    @property
    def api_key_configured(self) -> bool:
        """Return whether an API key is configured without exposing the secret."""

        return bool(self.api_key)

    def endpoint_for_tool(self, tool_name: str) -> str | None:
        """Return the remote endpoint configured for one tool, or the fallback."""

        if self.tool_endpoints and tool_name in self.tool_endpoints:
            return self.tool_endpoints[tool_name]

        return self.endpoint_url


@dataclass(frozen=True)
class McpRemoteRequestEnvelope:
    """Transport envelope for a remote MCP server call."""

    server_name: str
    endpoint_url: str
    tool_name: str
    correlation_id: str
    payload: dict[str, Any]
    timeout_seconds: int

    def to_http_json(self) -> dict[str, Any]:
        """Return the tool argument body sent through the MCP transport."""

        return {
            "server_name": self.server_name,
            "tool_name": self.tool_name,
            "correlation_id": self.correlation_id,
            "payload": self.payload,
        }
