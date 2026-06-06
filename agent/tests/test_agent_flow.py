from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from main import app


client = TestClient(app)


def _configure_foundry_readiness_environment(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv(
        "FOUNDRY_PROJECT_ENDPOINT",
        "https://example.services.ai.azure.com/api/projects/test",
    )
    monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "test-model")
    monkeypatch.setenv("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    monkeypatch.setenv("AZURE_RESOURCE_GROUP", "rg-test")
    monkeypatch.setenv("AZURE_AI_ACCOUNT_NAME", "foundry-test")
    monkeypatch.setenv("AZURE_AI_PROJECT_NAME", "project-test")


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
    order_tool = next(tool for tool in body if tool["name"] == "getOrderStatus")
    supplier_tool = next(tool for tool in body if tool["name"] == "sendSupplierNotification")
    assert order_tool["required_entities"] == ["order_id"]
    assert supplier_tool["required_entities"] == ["shipment_id"]


def test_mcp_config_endpoint_returns_safe_runtime_config() -> None:
    response = client.get("/mcp/config")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "mode": "mock",
        "server_name": "logic-apps-standard-mcp",
        "endpoint_configured": False,
        "api_key_configured": False,
        "timeout_seconds": 30,
    }


def test_mcp_executor_endpoint_returns_safe_diagnostics() -> None:
    response = client.get("/mcp/executor")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "mode": "mock",
        "executor_name": "MockMcpExecutor",
        "server_name": "logic-apps-standard-mcp",
        "endpoint_configured": False,
        "remote_transport": "not_configured",
    }


def test_foundry_agent_adapter_endpoint_returns_active_runtime_boundary() -> None:
    response = client.get("/foundry/agent-adapter")

    assert response.status_code == 200
    assert response.json() == {
        "name": "local-rule-based-agent",
        "runtime": "local",
        "implementation_status": "local_deterministic_planner",
    }


def test_agent_chat_selects_order_tool_without_calling_it() -> None:
    response = client.post(
        "/agent/chat",
        json={"user_message": "Check order ORD-1001", "correlation_id": "chat-corr-001"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correlation_id"] == "chat-corr-001"
    assert body["status"] == "tool_selected"
    assert body["tool_called"] is False
    assert body["selected_tool"] == "getOrderStatus"
    assert body["risk_decision"] == "allow"
    assert body["approval_required"] is False
    assert body["entities"] == {"order_id": "ORD-1001"}
    assert body["planned_action"] == {
        "tool_name": "getOrderStatus",
        "entities": {"order_id": "ORD-1001"},
        "risk_decision": "allow",
        "approval_required": False,
        "ready_for_simulation": True,
        "missing_entities": [],
    }
    assert body["simulation_result"] is None
    assert body["approval_request"] is None


def test_agent_chat_simulates_allowed_ready_tool_when_requested() -> None:
    response = client.post(
        "/agent/chat",
        json={
            "user_message": "Check order ORD-1001",
            "correlation_id": "chat-corr-002",
            "simulate_when_ready": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correlation_id"] == "chat-corr-002"
    assert body["status"] == "completed"
    assert body["tool_called"] is True
    assert body["selected_tool"] == "getOrderStatus"
    assert body["planned_action"]["ready_for_simulation"] is True
    assert body["simulation_result"]["tool_name"] == "getOrderStatus"
    assert body["simulation_result"]["correlation_id"] == "chat-corr-002"
    assert body["simulation_result"]["status"] == "completed"
    assert body["simulation_result"]["risk_decision"] == "allow"
    assert body["simulation_result"]["approval_required"] is False
    assert body["simulation_result"]["request_payload"] == {"order_id": "ORD-1001"}
    assert body["simulation_result"]["result"]["orderNumber"] == "4500098123"
    assert body["approval_request"] is None


def test_agent_chat_does_not_simulate_when_required_entities_are_missing() -> None:
    response = client.post(
        "/agent/chat",
        json={"user_message": "Check order status", "simulate_when_ready": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "missing_required_entities"
    assert body["tool_called"] is False
    assert body["selected_tool"] == "getOrderStatus"
    assert body["planned_action"]["ready_for_simulation"] is False
    assert body["planned_action"]["missing_entities"] == ["order_id"]
    assert body["simulation_result"] is None
    assert body["approval_request"] is None


def test_agent_chat_creates_approval_request_for_ready_high_risk_tool() -> None:
    response = client.post(
        "/agent/chat",
        json={
            "user_message": "Notify supplier about shipment SHIP-3001",
            "correlation_id": "chat-corr-003",
            "simulate_when_ready": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approval_required"
    assert body["correlation_id"] == "chat-corr-003"
    assert body["tool_called"] is False
    assert body["selected_tool"] == "sendSupplierNotification"
    assert body["risk_decision"] == "require_approval"
    assert body["approval_required"] is True
    assert body["planned_action"]["ready_for_simulation"] is True
    assert body["planned_action"]["missing_entities"] == []
    assert body["simulation_result"] is None
    assert body["approval_request"] == {
        "approval_id": "apr-chat-corr-003",
        "correlation_id": "chat-corr-003",
        "requested_tool": "sendSupplierNotification",
        "requested_entities": {"shipment_id": "SHIP-3001"},
        "status": "pending",
        "reason": "High-risk enterprise actions require human approval before execution.",
    }


def test_approval_decision_endpoint_approves_pending_request() -> None:
    client.post(
        "/agent/chat",
        json={
            "user_message": "Notify supplier about shipment SHIP-3002",
            "correlation_id": "chat-corr-004",
            "simulate_when_ready": True,
        },
    )

    response = client.post(
        "/approvals/apr-chat-corr-004/decision",
        json={
            "decision": "approved",
            "reviewer": "integration.manager@contoso.com",
            "comment": "Supplier notification is valid.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "approval_id": "apr-chat-corr-004",
        "correlation_id": "chat-corr-004",
        "requested_tool": "sendSupplierNotification",
        "decision": "approved",
        "status": "approved",
        "reviewer": "integration.manager@contoso.com",
        "comment": "Supplier notification is valid.",
    }


def test_approval_decision_endpoint_rejects_pending_request() -> None:
    client.post(
        "/agent/chat",
        json={
            "user_message": "Notify supplier about shipment SHIP-3003",
            "correlation_id": "chat-corr-005",
            "simulate_when_ready": True,
        },
    )

    response = client.post(
        "/approvals/apr-chat-corr-005/decision",
        json={
            "decision": "rejected",
            "reviewer": "integration.manager@contoso.com",
            "comment": "Need more business context.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["approval_id"] == "apr-chat-corr-005"
    assert body["decision"] == "rejected"
    assert body["status"] == "rejected"
    assert body["requested_tool"] == "sendSupplierNotification"
    assert body["comment"] == "Need more business context."


def test_approval_decision_endpoint_returns_404_for_unknown_request() -> None:
    response = client.post(
        "/approvals/apr-missing/decision",
        json={
            "decision": "approved",
            "reviewer": "integration.manager@contoso.com",
        },
    )

    assert response.status_code == 404


def test_execute_approved_action_simulates_original_high_risk_tool() -> None:
    client.post(
        "/agent/chat",
        json={
            "user_message": "Notify supplier about shipment SHIP-3004",
            "correlation_id": "chat-corr-006",
            "simulate_when_ready": True,
        },
    )
    client.post(
        "/approvals/apr-chat-corr-006/decision",
        json={
            "decision": "approved",
            "reviewer": "integration.manager@contoso.com",
            "comment": "Approved for supplier communication.",
        },
    )

    response = client.post("/approvals/apr-chat-corr-006/execute")

    assert response.status_code == 200
    body = response.json()
    assert body["approval_id"] == "apr-chat-corr-006"
    assert body["approval_status"] == "approved"
    assert body["execution_status"] == "completed"
    assert body["tool_name"] == "sendSupplierNotification"
    assert body["correlation_id"] == "chat-corr-006"
    assert body["simulation_result"]["tool_name"] == "sendSupplierNotification"
    assert body["simulation_result"]["status"] == "completed"
    assert body["simulation_result"]["risk_decision"] == "require_approval"
    assert body["simulation_result"]["approval_required"] is False
    assert body["simulation_result"]["request_payload"] == {"shipment_id": "SHIP-3004"}
    assert body["simulation_result"]["result"]["notificationId"] == "NOTIF-1001"
    assert body["simulation_result"]["result"]["status"] == "Sent"


def test_execute_approved_action_returns_404_for_unknown_approval() -> None:
    response = client.post("/approvals/apr-does-not-exist/execute")

    assert response.status_code == 404


def test_execute_approved_action_blocks_pending_approval() -> None:
    client.post(
        "/agent/chat",
        json={
            "user_message": "Notify supplier about shipment SHIP-3005",
            "correlation_id": "chat-corr-007",
            "simulate_when_ready": True,
        },
    )

    response = client.post("/approvals/apr-chat-corr-007/execute")

    assert response.status_code == 409
    assert "still pending" in response.json()["detail"]


def test_execute_approved_action_blocks_rejected_approval() -> None:
    client.post(
        "/agent/chat",
        json={
            "user_message": "Notify supplier about shipment SHIP-3006",
            "correlation_id": "chat-corr-008",
            "simulate_when_ready": True,
        },
    )
    client.post(
        "/approvals/apr-chat-corr-008/decision",
        json={
            "decision": "rejected",
            "reviewer": "integration.manager@contoso.com",
        },
    )

    response = client.post("/approvals/apr-chat-corr-008/execute")

    assert response.status_code == 409
    assert "rejected" in response.json()["detail"]


def test_audit_endpoint_returns_governed_workflow_events() -> None:
    client.post(
        "/agent/chat",
        json={
            "user_message": "Notify supplier about shipment SHIP-3007",
            "correlation_id": "chat-corr-009",
            "simulate_when_ready": True,
        },
    )
    client.post(
        "/approvals/apr-chat-corr-009/decision",
        json={
            "decision": "approved",
            "reviewer": "integration.manager@contoso.com",
            "comment": "Approved for audit test.",
        },
    )
    client.post("/approvals/apr-chat-corr-009/execute")

    response = client.get("/audit/chat-corr-009")

    assert response.status_code == 200
    body = response.json()
    event_types = [event["event_type"] for event in body]
    assert event_types == [
        "agent_chat_planned",
        "approval_request_created",
        "approval_decision_recorded",
        "approved_action_executed",
    ]
    assert body[0]["details"]["selected_tool"] == "sendSupplierNotification"
    assert body[1]["details"]["approval_id"] == "apr-chat-corr-009"
    assert body[2]["details"]["decision"] == "approved"
    assert body[3]["details"]["tool_name"] == "sendSupplierNotification"
    assert body[3]["details"]["request_payload"] == {"shipment_id": "SHIP-3007"}


def test_audit_endpoint_returns_empty_list_for_unknown_correlation() -> None:
    response = client.get("/audit/no-such-correlation")

    assert response.status_code == 200
    assert response.json() == []


def test_foundry_traces_endpoint_projects_audit_events() -> None:
    client.post(
        "/agent/chat",
        json={
            "user_message": "Notify supplier about shipment SHIP-3008",
            "correlation_id": "chat-corr-010",
            "simulate_when_ready": True,
        },
    )
    client.post(
        "/approvals/apr-chat-corr-010/decision",
        json={
            "decision": "approved",
            "reviewer": "integration.manager@contoso.com",
        },
    )
    client.post("/approvals/apr-chat-corr-010/execute")

    response = client.get("/foundry/traces/chat-corr-010")

    assert response.status_code == 200
    body = response.json()
    assert [trace["span_name"] for trace in body] == [
        "agent_chat_planned",
        "approval_request_created",
        "approval_decision_recorded",
        "approved_action_executed",
    ]
    assert [trace["span_kind"] for trace in body] == ["agent", "approval", "approval", "tool"]
    assert body[0]["correlation_id"] == "chat-corr-010"
    assert body[0]["attributes"]["selected_tool"] == "sendSupplierNotification"
    assert body[3]["attributes"]["risk_decision"] == "require_approval"


def test_appinsights_endpoint_projects_trace_events() -> None:
    client.post(
        "/agent/chat",
        json={
            "user_message": "Notify supplier about shipment SHIP-3009",
            "correlation_id": "chat-corr-011",
            "simulate_when_ready": True,
        },
    )

    response = client.get("/observability/appinsights/chat-corr-011")

    assert response.status_code == 200
    body = response.json()
    assert [event["name"] for event in body] == [
        "enterprise.integration.agent_chat_planned",
        "enterprise.integration.approval_request_created",
    ]
    assert body[0]["operation_id"] == "chat-corr-011"
    assert body[0]["severity"] == "warning"
    assert body[0]["properties"]["status"] == "approval_required"
    assert body[1]["properties"]["approval_id"] == "apr-chat-corr-011"


def test_evaluation_cases_endpoint_returns_safety_cases() -> None:
    response = client.get("/foundry/evaluations/safety-cases")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 4
    assert body[0]["case_id"] == "eval-order-ready"
    assert body[0]["expected"]["selected_tool"] == "getOrderStatus"
    assert body[2]["expected"]["approval_request_created"] is True


def test_run_local_evaluations_endpoint_returns_passing_results() -> None:
    response = client.post("/foundry/evaluations/run-local")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 4
    assert all(result["passed"] for result in body)
    assert all(result["failures"] == [] for result in body)


def test_operations_readiness_endpoint_returns_ready_report(monkeypatch: MonkeyPatch) -> None:
    _configure_foundry_readiness_environment(monkeypatch)
    response = client.get("/operations/readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    check_names = {check["name"] for check in body["checks"]}
    assert check_names == {
        "tool_catalog",
        "high_risk_policy",
        "approval_store",
        "audit_store",
        "observability_projection",
        "mcp_runtime_config",
        "agent_runtime_adapter",
        "foundry_agent_definition",
        "foundry_tool_registration",
        "maf_agent_skeleton",
        "foundry_registration_preflight",
        "environment_validation",
    }


def test_operations_environment_endpoint_returns_validation_report(monkeypatch: MonkeyPatch) -> None:
    _configure_foundry_readiness_environment(monkeypatch)
    response = client.get("/operations/environment")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    checks = {check["name"]: check for check in body["checks"]}
    assert checks["agent_runtime_mode"]["status"] == "pass"
    assert checks["mcp_mode"]["status"] == "pass"
    assert checks["remote_mcp_endpoint"]["status"] == "skip"
    assert checks["remote_mcp_auth"]["status"] == "skip"
    assert checks["foundry_runtime"]["status"] == "pass"
    assert checks["foundry_resource_context"]["status"] == "pass"
    assert checks["appinsights"]["status"] == "warning"


def test_agent_chat_selects_invoice_tool_and_generates_correlation_id() -> None:
    response = client.post("/agent/chat", json={"user_message": "Validate invoice INV-2001"})

    assert response.status_code == 200
    body = response.json()
    assert body["correlation_id"]
    assert body["tool_called"] is False
    assert body["selected_tool"] == "validateInvoice"
    assert body["risk_decision"] == "allow"
    assert body["entities"] == {"invoice_id": "INV-2001"}
    assert body["planned_action"]["tool_name"] == "validateInvoice"
    assert body["planned_action"]["ready_for_simulation"] is True
    assert body["planned_action"]["missing_entities"] == []


def test_agent_chat_marks_high_risk_selected_tool_as_approval_required() -> None:
    response = client.post(
        "/agent/chat",
        json={"user_message": "Notify supplier about shipment delay"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["selected_tool"] == "sendSupplierNotification"
    assert body["risk_decision"] == "require_approval"
    assert body["approval_required"] is True
    assert body["tool_called"] is False
    assert body["planned_action"]["tool_name"] == "sendSupplierNotification"
    assert body["planned_action"]["approval_required"] is True
    assert body["planned_action"]["ready_for_simulation"] is False
    assert body["planned_action"]["missing_entities"] == ["shipment_id"]
    assert body["approval_request"] is None


def test_agent_chat_extracts_shipment_id() -> None:
    response = client.post(
        "/agent/chat",
        json={"user_message": "Check shipment status for SHIP-3001"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["selected_tool"] == "checkShipmentStatus"
    assert body["entities"] == {"shipment_id": "SHIP-3001"}
    assert body["planned_action"]["ready_for_simulation"] is True
    assert body["planned_action"]["missing_entities"] == []


def test_agent_chat_extracts_correlation_id_for_run_status() -> None:
    response = client.post(
        "/agent/chat",
        json={"user_message": "Check integration run status for correlation demo-corr-001"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["selected_tool"] == "queryIntegrationRunStatus"
    assert body["entities"] == {"correlation_id": "demo-corr-001"}
    assert body["planned_action"]["ready_for_simulation"] is True
    assert body["planned_action"]["missing_entities"] == []


def test_agent_chat_marks_order_plan_not_ready_without_order_id() -> None:
    response = client.post("/agent/chat", json={"user_message": "Check order status"})

    assert response.status_code == 200
    body = response.json()
    assert body["selected_tool"] == "getOrderStatus"
    assert body["planned_action"]["ready_for_simulation"] is False
    assert body["planned_action"]["missing_entities"] == ["order_id"]


def test_agent_chat_returns_clarification_when_no_tool_matches() -> None:
    response = client.post("/agent/chat", json={"user_message": "Tell me a joke"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "needs_clarification"
    assert body["selected_tool"] is None
    assert body["tool_called"] is False
    assert body["entities"] == {}
    assert body["planned_action"] is None


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
    assert body["request_payload"] is None
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
