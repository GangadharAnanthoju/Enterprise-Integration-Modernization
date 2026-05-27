from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tools_endpoint_returns_catalog() -> None:
    response = client.get("/tools")

    assert response.status_code == 200
    body = response.json()
    tool_names = {tool["name"] for tool in body}

    assert len(body) == 7
    assert "getOrderStatus" in tool_names
    assert "sendSupplierNotification" in tool_names


def test_agent_chat_placeholder_receives_message_without_calling_tools() -> None:
    response = client.post(
        "/agent/chat",
        json={"user_message": "Check order ORD-1001", "correlation_id": "chat-corr-001"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correlation_id"] == "chat-corr-001"
    assert body["status"] == "received"
    assert body["tool_called"] is False
    assert "Agent shell received your request" in body["message"]


def test_agent_chat_placeholder_generates_correlation_id() -> None:
    response = client.post("/agent/chat", json={"user_message": "Validate invoice INV-2001"})

    assert response.status_code == 200
    body = response.json()
    assert body["correlation_id"]
    assert body["tool_called"] is False


def test_single_tool_endpoint_returns_risk_metadata() -> None:
    response = client.get("/tools/sendSupplierNotification")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "sendSupplierNotification"
    assert body["risk_level"] == "high"
    assert body["approval_required"] is True


def test_unknown_tool_endpoint_returns_404() -> None:
    response = client.get("/tools/deletePurchaseOrder")

    assert response.status_code == 404


def test_tool_risk_endpoint_returns_allow_decision_for_low_risk_tool() -> None:
    response = client.get("/tools/getOrderStatus/risk")

    assert response.status_code == 200
    body = response.json()
    assert body["tool_name"] == "getOrderStatus"
    assert body["risk_level"] == "low"
    assert body["decision"] == "allow"
    assert body["approval_required"] is False
    assert body["audit_required"] is True


def test_tool_risk_endpoint_returns_approval_decision_for_high_risk_tool() -> None:
    response = client.get("/tools/sendSupplierNotification/risk")

    assert response.status_code == 200
    body = response.json()
    assert body["tool_name"] == "sendSupplierNotification"
    assert body["risk_level"] == "high"
    assert body["decision"] == "require_approval"
    assert body["approval_required"] is True
    assert body["audit_required"] is True


def test_unknown_tool_risk_endpoint_returns_404() -> None:
    response = client.get("/tools/deletePurchaseOrder/risk")

    assert response.status_code == 404


def test_simulate_endpoint_returns_sample_data_for_allowed_tool() -> None:
    response = client.post("/tools/getOrderStatus/simulate")

    assert response.status_code == 200
    body = response.json()
    assert body["tool_name"] == "getOrderStatus"
    assert body["correlation_id"]
    assert body["mode"] == "mock"
    assert body["status"] == "completed"
    assert body["risk_decision"] == "allow"
    assert body["approval_required"] is False
    assert body["result"]["orderNumber"] == "4500098123"


def test_simulate_endpoint_stops_high_risk_tool_for_approval() -> None:
    response = client.post(
        "/tools/sendSupplierNotification/simulate",
        json={"correlation_id": "demo-corr-001"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tool_name"] == "sendSupplierNotification"
    assert body["correlation_id"] == "demo-corr-001"
    assert body["mode"] == "mock"
    assert body["status"] == "approval_required"
    assert body["risk_decision"] == "require_approval"
    assert body["approval_required"] is True
    assert body["result"] is None


def test_unknown_tool_simulate_endpoint_returns_404() -> None:
    response = client.post("/tools/deletePurchaseOrder/simulate")

    assert response.status_code == 404


def test_simulate_endpoint_accepts_caller_correlation_id() -> None:
    response = client.post(
        "/tools/getOrderStatus/simulate",
        json={"correlation_id": "demo-corr-002"},
    )

    assert response.status_code == 200
    assert response.json()["correlation_id"] == "demo-corr-002"
