from config import Settings
from foundry.agent_adapter import MafFoundryAgentAdapter, get_agent_adapter
from foundry.evaluations import list_evaluation_cases, run_local_evaluation_suite
from foundry.live_agent import FoundryAgentInvocationResult


def test_agent_adapter_wraps_current_rule_based_agent_shell() -> None:
    adapter = get_agent_adapter()

    result = adapter.chat(
        user_message="Check order ORD-1001",
        correlation_id="adapter-corr-001",
        simulate_when_ready=True,
    )

    assert adapter.name == "local-rule-based-agent"
    assert adapter.runtime == "local"
    assert adapter.implementation_status == "local_deterministic_planner"
    assert result.correlation_id == "adapter-corr-001"
    assert result.status == "completed"
    assert result.selected_tool == "getOrderStatus"
    assert result.simulation_result is not None
    assert result.simulation_result.request is not None
    assert result.simulation_result.request.payload == {"order_id": "ORD-1001"}


def test_agent_adapter_can_select_foundry_runtime_from_settings() -> None:
    adapter = get_agent_adapter(
        Settings(
            _env_file=None,
            agent_runtime_mode="foundry",
            foundry_agent_name="enterprise-integration-agent",
        )
    )

    assert adapter.name == "enterprise-integration-agent"
    assert adapter.runtime == "microsoft_foundry"
    assert adapter.implementation_status == "live_foundry_structured_planning_only"


def test_foundry_adapter_returns_plan_when_simulation_not_requested() -> None:
    def fake_invoker(message: str) -> FoundryAgentInvocationResult:
        return FoundryAgentInvocationResult(
            agent_name="enterprise-integration-agent",
            agent_version="2",
            project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            input_text=message,
            response_text="""
            {
              "selected_tool": "getOrderStatus",
              "entities": {"order_id": "ORD-1001"},
              "requires_clarification": false,
              "clarification_question": null,
              "confidence": "high",
              "reason": "The user asked to check order status."
            }
            """,
            response_id="resp-123",
            raw={},
        )

    adapter = MafFoundryAgentAdapter(runtime_invoker=fake_invoker)

    result = adapter.chat(
        user_message="Check order ORD-1001",
        correlation_id="foundry-corr-001",
        simulate_when_ready=False,
    )

    assert result.correlation_id == "foundry-corr-001"
    assert result.status == "tool_selected"
    assert result.tool_called is False
    assert result.selected_tool == "getOrderStatus"
    assert result.risk_decision == "allow"
    assert result.approval_required is False
    assert result.entities == {"order_id": "ORD-1001"}
    assert result.planned_action is not None
    assert result.planned_action.tool_name == "getOrderStatus"
    assert result.planned_action.ready_for_simulation is True
    assert result.planned_action.missing_entities == []
    assert result.simulation_result is None
    assert result.approval_request is None


def test_foundry_adapter_executes_ready_allowed_plan_when_requested() -> None:
    def fake_invoker(message: str) -> FoundryAgentInvocationResult:
        return FoundryAgentInvocationResult(
            agent_name="enterprise-integration-agent",
            agent_version="2",
            project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            input_text=message,
            response_text="""
            {
              "selected_tool": "getOrderStatus",
              "entities": {"order_id": "ORD-1001"},
              "requires_clarification": false,
              "clarification_question": null,
              "confidence": "high",
              "reason": "The user asked to check order status."
            }
            """,
            response_id="resp-126",
            raw={},
        )

    adapter = MafFoundryAgentAdapter(runtime_invoker=fake_invoker)

    result = adapter.chat(
        user_message="Check order ORD-1001",
        correlation_id="foundry-corr-004",
        simulate_when_ready=True,
    )

    assert result.status == "completed"
    assert result.tool_called is True
    assert result.selected_tool == "getOrderStatus"
    assert result.simulation_result is not None
    assert result.simulation_result.request is not None
    assert result.simulation_result.request.payload == {"order_id": "ORD-1001"}
    assert result.approval_request is None


def test_foundry_adapter_returns_missing_entities_from_parsed_plan() -> None:
    def fake_invoker(message: str) -> FoundryAgentInvocationResult:
        return FoundryAgentInvocationResult(
            agent_name="enterprise-integration-agent",
            agent_version="2",
            project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            input_text=message,
            response_text="""
            {
              "selected_tool": "getOrderStatus",
              "entities": {},
              "requires_clarification": true,
              "clarification_question": "Please provide the order ID.",
              "confidence": "medium",
              "reason": "The user asked for order status without an order ID."
            }
            """,
            response_id="resp-124",
            raw={},
        )

    adapter = MafFoundryAgentAdapter(runtime_invoker=fake_invoker)

    result = adapter.chat(
        user_message="Check order status",
        correlation_id="foundry-corr-002",
        simulate_when_ready=True,
    )

    assert result.status == "missing_required_entities"
    assert result.message == "Please provide the order ID."
    assert result.selected_tool == "getOrderStatus"
    assert result.planned_action is not None
    assert result.planned_action.ready_for_simulation is False
    assert result.planned_action.missing_entities == ["order_id"]
    assert result.simulation_result is None


def test_foundry_adapter_creates_approval_for_high_risk_plan() -> None:
    def fake_invoker(message: str) -> FoundryAgentInvocationResult:
        return FoundryAgentInvocationResult(
            agent_name="enterprise-integration-agent",
            agent_version="2",
            project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            input_text=message,
            response_text="""
            {
              "selected_tool": "sendSupplierNotification",
              "entities": {"shipment_id": "SHIP-3001"},
              "requires_clarification": false,
              "clarification_question": null,
              "confidence": "high",
              "reason": "The user asked to notify a supplier."
            }
            """,
            response_id="resp-127",
            raw={},
        )

    adapter = MafFoundryAgentAdapter(runtime_invoker=fake_invoker)

    result = adapter.chat(
        user_message="Notify supplier about shipment SHIP-3001",
        correlation_id="foundry-corr-005",
        simulate_when_ready=True,
    )

    assert result.status == "approval_required"
    assert result.tool_called is False
    assert result.selected_tool == "sendSupplierNotification"
    assert result.risk_decision == "require_approval"
    assert result.approval_request is not None
    assert result.approval_request.approval_id == "apr-foundry-corr-005"


def test_foundry_adapter_rejects_invalid_plan_without_backend_execution() -> None:
    def fake_invoker(message: str) -> FoundryAgentInvocationResult:
        return FoundryAgentInvocationResult(
            agent_name="enterprise-integration-agent",
            agent_version="2",
            project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            input_text=message,
            response_text="Selected tool: getOrderStatus",
            response_id="resp-125",
            raw={},
        )

    adapter = MafFoundryAgentAdapter(runtime_invoker=fake_invoker)

    result = adapter.chat(
        user_message="Check order ORD-1001",
        correlation_id="foundry-corr-003",
        simulate_when_ready=True,
    )

    assert result.status == "foundry_plan_invalid"
    assert result.tool_called is False
    assert result.selected_tool is None
    assert result.planned_action is None
    assert result.simulation_result is None


def test_local_evaluation_cases_cover_core_governance_paths() -> None:
    cases = list_evaluation_cases()
    case_ids = {case.case_id for case in cases}

    assert case_ids == {
        "eval-order-ready",
        "eval-order-missing-id",
        "eval-supplier-approval",
        "eval-unknown-intent",
    }


def test_local_evaluation_suite_passes_current_agent_shell() -> None:
    results = run_local_evaluation_suite()

    assert results
    assert all(result.passed for result in results)
    assert all(result.failures == [] for result in results)
