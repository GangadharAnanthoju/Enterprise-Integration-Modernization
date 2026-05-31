from agent_execution import execute_planned_action, get_missing_entities


def test_get_missing_entities_uses_tool_contract() -> None:
    assert get_missing_entities("getOrderStatus", {}) == ["order_id"]
    assert get_missing_entities("getOrderStatus", {"order_id": "ORD-1001"}) == []


def test_execute_planned_action_returns_plan_only_by_default() -> None:
    result = execute_planned_action(
        selected_tool="getOrderStatus",
        entities={"order_id": "ORD-1001"},
        correlation_id="exec-corr-001",
    )

    assert result.status == "tool_selected"
    assert result.tool_called is False
    assert result.selected_tool == "getOrderStatus"
    assert result.risk_decision == "allow"
    assert result.planned_action is not None
    assert result.planned_action.ready_for_simulation is True
    assert result.simulation_result is None


def test_execute_planned_action_runs_allowed_ready_tool_when_requested() -> None:
    result = execute_planned_action(
        selected_tool="getOrderStatus",
        entities={"order_id": "ORD-1001"},
        correlation_id="exec-corr-002",
        simulate_when_ready=True,
    )

    assert result.status == "completed"
    assert result.tool_called is True
    assert result.simulation_result is not None
    assert result.simulation_result.request is not None
    assert result.simulation_result.request.payload == {"order_id": "ORD-1001"}


def test_execute_planned_action_blocks_missing_entities() -> None:
    result = execute_planned_action(
        selected_tool="getOrderStatus",
        entities={},
        correlation_id="exec-corr-003",
        simulate_when_ready=True,
    )

    assert result.status == "missing_required_entities"
    assert result.tool_called is False
    assert result.planned_action is not None
    assert result.planned_action.ready_for_simulation is False
    assert result.planned_action.missing_entities == ["order_id"]


def test_execute_planned_action_creates_approval_for_high_risk_tool() -> None:
    result = execute_planned_action(
        selected_tool="sendSupplierNotification",
        entities={"shipment_id": "SHIP-3001"},
        correlation_id="exec-corr-004",
        simulate_when_ready=True,
    )

    assert result.status == "approval_required"
    assert result.tool_called is False
    assert result.approval_required is True
    assert result.approval_request is not None
    assert result.approval_request.approval_id == "apr-exec-corr-004"


def test_execute_planned_action_rejects_unsupported_tool() -> None:
    result = execute_planned_action(
        selected_tool="deletePurchaseOrder",
        entities={"order_id": "ORD-1001"},
        correlation_id="exec-corr-005",
        simulate_when_ready=True,
    )

    assert result.status == "unsupported_tool"
    assert result.tool_called is False
    assert result.planned_action is None
    assert result.simulation_result is None
