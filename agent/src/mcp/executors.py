"""MCP execution adapters.

The client builds validated MCP requests. Executors decide how those requests
are fulfilled: local sample data today, remote Logic Apps Standard MCP later.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from mcp.exceptions import RemoteMcpConfigurationError
from mcp.remote import RemoteMcpHttpClient, build_remote_request_envelope
from mcp.schemas import McpExecutionMode, McpServerConfig, McpToolRequest
from tools.contracts import ToolContract


@dataclass(frozen=True)
class McpExecutionOutput:
    """Normalized output from any MCP executor."""

    mode: str
    status: str
    result: dict[str, Any] | None
    message: str


@dataclass(frozen=True)
class McpExecutorDiagnostics:
    """Diagnostic metadata for the active MCP executor."""

    mode: str
    executor_name: str
    server_name: str
    endpoint_configured: bool
    remote_transport: str


class McpExecutor(Protocol):
    """Stable execution interface for mock and remote MCP runtimes."""

    mode: McpExecutionMode

    def execute(self, tool: ToolContract, request: McpToolRequest | None) -> McpExecutionOutput:
        """Execute one approved MCP tool request."""


@dataclass(frozen=True)
class MockMcpExecutor:
    """Local executor that returns sample responses without network calls."""

    mode: McpExecutionMode = McpExecutionMode.MOCK

    def execute(self, tool: ToolContract, request: McpToolRequest | None) -> McpExecutionOutput:
        """Return the local sample response for the approved tool."""

        return McpExecutionOutput(
            mode=self.mode.value,
            status="completed",
            result=_load_sample_response(tool),
            message="Tool simulation completed using the local sample response.",
        )


@dataclass(frozen=True)
class RemoteMcpExecutor:
    """Placeholder for future Logic Apps Standard MCP execution."""

    config: McpServerConfig
    http_client: RemoteMcpHttpClient | None = None
    mode: McpExecutionMode = McpExecutionMode.REMOTE

    def execute(self, tool: ToolContract, request: McpToolRequest | None) -> McpExecutionOutput:
        """Fail safely until the real remote MCP transport is implemented."""

        if request is None:
            raise RemoteMcpConfigurationError(self.config.server_name)

        if not self.config.endpoint_configured:
            raise RemoteMcpConfigurationError(self.config.server_name)

        envelope = build_remote_request_envelope(self.config, request)
        client = self.http_client or RemoteMcpHttpClient(self.config)
        response = client.send(envelope)
        return McpExecutionOutput(
            mode=self.mode.value,
            status=str(response.get("status", "completed")),
            result=response.get("result") if isinstance(response.get("result"), dict) else None,
            message=str(response.get("message", "Remote MCP execution completed.")),
        )


def get_mcp_executor(config: McpServerConfig) -> McpExecutor:
    """Return the executor for the configured MCP runtime mode."""

    if config.mode == McpExecutionMode.MOCK:
        return MockMcpExecutor()

    return RemoteMcpExecutor(config=config)


def get_mcp_executor_diagnostics(config: McpServerConfig) -> McpExecutorDiagnostics:
    """Return safe diagnostic metadata for the configured MCP executor."""

    executor = get_mcp_executor(config)
    return McpExecutorDiagnostics(
        mode=config.mode.value,
        executor_name=executor.__class__.__name__,
        server_name=config.server_name,
        endpoint_configured=config.endpoint_configured,
        remote_transport=(
            "not_configured"
            if config.mode == McpExecutionMode.MOCK
            else "httpx"
        ),
    )


def _repo_root() -> Path:
    """Return the repository root from this source file location."""

    return Path(__file__).resolve().parents[3]


def _load_sample_response(tool: ToolContract) -> dict[str, Any]:
    """Load the sample Logic Apps response for a tool."""

    response_path = _repo_root() / tool.output_schema_ref
    with response_path.open(encoding="utf-8") as response_file:
        return json.load(response_file)
