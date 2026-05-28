class McpToolError(Exception):
    """Raised when an MCP tool call fails."""


class MissingRequiredEntitiesError(McpToolError):
    """Raised when an MCP request cannot be built from incomplete entities."""

    def __init__(self, tool_name: str, missing_entities: list[str]) -> None:
        self.tool_name = tool_name
        self.missing_entities = missing_entities
        missing = ", ".join(missing_entities)
        super().__init__(f"Missing required entities for {tool_name}: {missing}")
