class McpToolError(Exception):
    """Raised when an MCP tool call fails."""


class MissingRequiredEntitiesError(McpToolError):
    """Raised when an MCP request cannot be built from incomplete entities."""

    def __init__(self, tool_name: str, missing_entities: list[str]) -> None:
        self.tool_name = tool_name
        self.missing_entities = missing_entities
        missing = ", ".join(missing_entities)
        super().__init__(f"Missing required entities for {tool_name}: {missing}")


class RemoteMcpConfigurationError(McpToolError):
    """Raised when remote MCP mode is selected without required settings."""

    def __init__(self, server_name: str) -> None:
        self.server_name = server_name
        super().__init__(f"Remote MCP server endpoint is not configured for {server_name}.")


class RemoteMcpNotImplementedError(McpToolError):
    """Raised until real remote MCP transport is implemented."""

    def __init__(self, server_name: str, endpoint_url: str) -> None:
        self.server_name = server_name
        self.endpoint_url = endpoint_url
        super().__init__(
            f"Remote MCP execution is not implemented for {server_name} at {endpoint_url}."
        )


class RemoteMcpTimeoutError(McpToolError):
    """Raised when remote MCP execution times out."""

    def __init__(self, server_name: str, timeout_seconds: int) -> None:
        self.server_name = server_name
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Remote MCP execution timed out for {server_name} after {timeout_seconds} seconds."
        )


class RemoteMcpAuthenticationError(McpToolError):
    """Raised when remote MCP authentication or authorization fails."""

    def __init__(self, server_name: str, status_code: int) -> None:
        self.server_name = server_name
        self.status_code = status_code
        super().__init__(
            f"Remote MCP authentication failed for {server_name} with status {status_code}."
        )


class RemoteMcpBackendError(McpToolError):
    """Raised when the remote MCP server reports a backend failure."""

    def __init__(self, server_name: str, status_code: int, detail: str) -> None:
        self.server_name = server_name
        self.status_code = status_code
        self.detail = detail
        super().__init__(
            f"Remote MCP backend failed for {server_name} with status {status_code}: {detail}"
        )
