import json

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


def test_remote_request_envelope_prefers_per_tool_endpoint() -> None:
    config = McpServerConfig(
        mode=McpExecutionMode.REMOTE,
        server_name="logic-apps-prod-mcp",
        endpoint_url="https://example.contoso/default",
        timeout_seconds=45,
        tool_endpoints={
            "getOrderStatus": "https://example.contoso/get-order-status",
        },
    )
    request = McpToolRequest(
        tool_name="getOrderStatus",
        correlation_id="remote-corr-001",
        payload={"order_id": "ORD-1001"},
    )

    envelope = build_remote_request_envelope(config, request)

    assert envelope.endpoint_url == "https://example.contoso/get-order-status"


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
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        body = json.loads(request.read())
        if body["method"] == "initialize":
            return httpx.Response(
                200,
                headers={"Mcp-Session-Id": "session-123"},
                json={
                    "jsonrpc": "2.0",
                    "id": body["id"],
                    "result": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "logic-apps-prod-mcp"},
                    },
                },
            )
        if body["method"] == "notifications/initialized":
            return httpx.Response(202)

        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": body["id"],
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "status": "completed",
                                    "result": {"orderNumber": "4500098123"},
                                    "message": "Remote MCP execution completed.",
                                }
                            ),
                        }
                    ],
                    "isError": False,
                },
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
    assert len(captured_requests) == 3
    tool_call_request = captured_requests[2]
    assert tool_call_request.url == "https://example.contoso/mcp"
    assert tool_call_request.headers["X-API-Key"] == "secret-token"
    assert tool_call_request.headers["X-Correlation-ID"] == "remote-corr-003"
    assert tool_call_request.headers["MCP-Protocol-Version"] == "2025-06-18"
    assert tool_call_request.headers["Mcp-Session-Id"] == "session-123"

    body = json.loads(tool_call_request.read())
    assert body["method"] == "tools/call"
    assert body["params"] == {
        "name": "getOrderStatus",
        "arguments": {
            "server_name": "logic-apps-prod-mcp",
            "tool_name": "getOrderStatus",
            "correlation_id": "remote-corr-003",
            "payload": {"order_id": "ORD-1001"},
        },
    }


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
            lambda request: _mock_mcp_response(
                request,
                result={
                    "status": "completed",
                    "result": {"orderNumber": "4500098123"},
                    "message": "Remote execution completed.",
                },
            ),
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


def _mock_mcp_response(request: httpx.Request, *, result: dict[str, object]) -> httpx.Response:
    """Return a small MCP JSON-RPC response for remote executor tests."""

    body = json.loads(request.read())
    if body["method"] == "initialize":
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": body["id"],
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "logic-apps-prod-mcp"},
                },
            },
        )
    if body["method"] == "notifications/initialized":
        return httpx.Response(202)

    return httpx.Response(
        200,
        json={
            "jsonrpc": "2.0",
            "id": body["id"],
            "result": {
                "content": [{"type": "text", "text": json.dumps(result)}],
                "isError": False,
            },
        },
    )


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
