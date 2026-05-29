import pytest
import httpx

from mcp.exceptions import (
    RemoteMcpAuthenticationError,
    RemoteMcpConfigurationError,
    RemoteMcpTimeoutError,
)
from mcp.executors import (
    MockMcpExecutor,
    RemoteMcpExecutor,
    get_mcp_executor,
    get_mcp_executor_diagnostics,
)
from mcp.remote import RemoteMcpHttpClient, build_remote_request_envelope, map_remote_http_error
from mcp.schemas import McpExecutionMode, McpServerConfig, McpToolRequest
from tools.registry import require_tool


def test_get_mcp_executor_returns_mock_executor_for_mock_mode() -> None:
    config = McpServerConfig(
        mode=McpExecutionMode.MOCK,
        server_name="logic-apps-standard-mcp",
        endpoint_url=None,
        timeout_seconds=30,
    )

    executor = get_mcp_executor(config)

    assert isinstance(executor, MockMcpExecutor)


def test_mock_mcp_executor_returns_local_sample_response() -> None:
    tool = require_tool("getOrderStatus")
    executor = MockMcpExecutor()

    output = executor.execute(tool, request=None)

    assert output.mode == "mock"
    assert output.status == "completed"
    assert output.result is not None
    assert output.result["orderNumber"] == "4500098123"


def test_get_mcp_executor_returns_remote_executor_for_remote_mode() -> None:
    config = McpServerConfig(
        mode=McpExecutionMode.REMOTE,
        server_name="logic-apps-prod-mcp",
        endpoint_url="https://example.contoso/mcp",
        timeout_seconds=45,
    )

    executor = get_mcp_executor(config)

    assert isinstance(executor, RemoteMcpExecutor)


def test_remote_request_envelope_wraps_validated_mcp_request() -> None:
    config = McpServerConfig(
        mode=McpExecutionMode.REMOTE,
        server_name="logic-apps-prod-mcp",
        endpoint_url="https://example.contoso/mcp",
        timeout_seconds=45,
    )
    request = McpToolRequest(
        tool_name="getOrderStatus",
        correlation_id="remote-corr-001",
        payload={"order_id": "ORD-1001"},
    )

    envelope = build_remote_request_envelope(config, request)

    assert envelope.server_name == "logic-apps-prod-mcp"
    assert envelope.endpoint_url == "https://example.contoso/mcp"
    assert envelope.tool_name == "getOrderStatus"
    assert envelope.correlation_id == "remote-corr-001"
    assert envelope.payload == {"order_id": "ORD-1001"}
    assert envelope.timeout_seconds == 45
    assert envelope.to_http_json() == {
        "server_name": "logic-apps-prod-mcp",
        "tool_name": "getOrderStatus",
        "correlation_id": "remote-corr-001",
        "payload": {"order_id": "ORD-1001"},
    }


def test_remote_mcp_executor_requires_endpoint_configuration() -> None:
    tool = require_tool("getOrderStatus")
    executor = RemoteMcpExecutor(
        config=McpServerConfig(
            mode=McpExecutionMode.REMOTE,
            server_name="logic-apps-prod-mcp",
            endpoint_url=None,
            timeout_seconds=45,
        )
    )

    with pytest.raises(RemoteMcpConfigurationError) as exc_info:
        executor.execute(
            tool,
            request=McpToolRequest(
                tool_name="getOrderStatus",
                correlation_id="remote-corr-002",
                payload={"order_id": "ORD-1001"},
            ),
        )

    assert exc_info.value.server_name == "logic-apps-prod-mcp"


def test_remote_mcp_http_client_posts_envelope_with_safe_auth_headers() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "result": {"orderNumber": "4500098123"},
                "message": "Remote MCP execution completed.",
            },
        )

    config = McpServerConfig(
        mode=McpExecutionMode.REMOTE,
        server_name="logic-apps-prod-mcp",
        endpoint_url="https://example.contoso/mcp",
        timeout_seconds=45,
        api_key="secret-token",
    )
    client = RemoteMcpHttpClient(config, transport=httpx.MockTransport(handler))
    envelope = build_remote_request_envelope(
        config,
        McpToolRequest(
            tool_name="getOrderStatus",
            correlation_id="remote-corr-003",
            payload={"order_id": "ORD-1001"},
        ),
    )

    response = client.send(envelope)

    assert response["status"] == "completed"
    assert response["result"] == {"orderNumber": "4500098123"}
    assert captured_request is not None
    assert captured_request.url == "https://example.contoso/mcp"
    assert captured_request.headers["Authorization"] == "Bearer secret-token"
    assert captured_request.headers["X-Correlation-ID"] == "remote-corr-003"
    assert captured_request.headers["X-MCP-Tool-Name"] == "getOrderStatus"
    assert captured_request.read() == (
        b'{"server_name":"logic-apps-prod-mcp","tool_name":"getOrderStatus",'
        b'"correlation_id":"remote-corr-003","payload":{"order_id":"ORD-1001"}}'
    )


def test_remote_mcp_executor_returns_normalized_remote_output() -> None:
    tool = require_tool("getOrderStatus")
    config = McpServerConfig(
        mode=McpExecutionMode.REMOTE,
        server_name="logic-apps-prod-mcp",
        endpoint_url="https://example.contoso/mcp",
        timeout_seconds=45,
    )
    http_client = RemoteMcpHttpClient(
        config,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "status": "completed",
                    "result": {"orderNumber": "4500098123"},
                    "message": "Remote execution completed.",
                },
            )
        ),
    )
    executor = RemoteMcpExecutor(
        config=config,
        http_client=http_client,
    )

    output = executor.execute(
        tool,
        request=McpToolRequest(
            tool_name="getOrderStatus",
            correlation_id="remote-corr-004",
            payload={"order_id": "ORD-1001"},
        ),
    )

    assert output.mode == "remote"
    assert output.status == "completed"
    assert output.result == {"orderNumber": "4500098123"}
    assert output.message == "Remote execution completed."


def test_remote_mcp_http_client_maps_auth_and_timeout_failures() -> None:
    auth_config = McpServerConfig(
        mode=McpExecutionMode.REMOTE,
        server_name="logic-apps-prod-mcp",
        endpoint_url="https://example.contoso/mcp",
        timeout_seconds=45,
    )
    envelope = build_remote_request_envelope(
        auth_config,
        McpToolRequest(
            tool_name="getOrderStatus",
            correlation_id="remote-corr-005",
            payload={"order_id": "ORD-1001"},
        )
    )

    auth_client = RemoteMcpHttpClient(
        auth_config,
        transport=httpx.MockTransport(lambda request: httpx.Response(401, text="Unauthorized")),
    )
    timeout_client = RemoteMcpHttpClient(
        auth_config,
        transport=httpx.MockTransport(
            lambda request: (_ for _ in ()).throw(httpx.TimeoutException("timeout"))
        ),
    )

    with pytest.raises(RemoteMcpAuthenticationError):
        auth_client.send(envelope)

    with pytest.raises(RemoteMcpTimeoutError):
        timeout_client.send(envelope)


def test_mcp_executor_diagnostics_describe_active_executor() -> None:
    config = McpServerConfig(
        mode=McpExecutionMode.REMOTE,
        server_name="logic-apps-prod-mcp",
        endpoint_url="https://example.contoso/mcp",
        timeout_seconds=45,
    )

    diagnostics = get_mcp_executor_diagnostics(config)

    assert diagnostics.mode == "remote"
    assert diagnostics.executor_name == "RemoteMcpExecutor"
    assert diagnostics.server_name == "logic-apps-prod-mcp"
    assert diagnostics.endpoint_configured is True
    assert diagnostics.remote_transport == "httpx"


def test_remote_http_error_mapping_uses_specific_exception_types() -> None:
    auth_error = map_remote_http_error(
        server_name="logic-apps-prod-mcp",
        status_code=401,
        detail="Unauthorized",
        timeout_seconds=45,
    )
    timeout_error = map_remote_http_error(
        server_name="logic-apps-prod-mcp",
        status_code=504,
        detail="Gateway timeout",
        timeout_seconds=45,
    )
    backend_error = map_remote_http_error(
        server_name="logic-apps-prod-mcp",
        status_code=500,
        detail="Workflow failed",
        timeout_seconds=45,
    )

    assert auth_error.__class__.__name__ == "RemoteMcpAuthenticationError"
    assert timeout_error.__class__.__name__ == "RemoteMcpTimeoutError"
    assert backend_error.__class__.__name__ == "RemoteMcpBackendError"
