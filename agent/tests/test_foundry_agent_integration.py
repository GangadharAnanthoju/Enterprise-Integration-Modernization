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
    assert adapter.implementation_status == "temporary_rule_based"
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
    assert adapter.implementation_status == "live_foundry_invocation_planning_only"


def test_foundry_adapter_returns_live_response_without_backend_execution() -> None:
    def fake_invoker(message: str) -> FoundryAgentInvocationResult:
        return FoundryAgentInvocationResult(
            agent_name="enterprise-integration-agent",
            agent_version="1",
            project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            input_text=message,
            response_text="Selected tool: getOrderStatus",
            response_id="resp-123",
            raw={},
        )

    adapter = MafFoundryAgentAdapter(runtime_invoker=fake_invoker)

    result = adapter.chat(
        user_message="Check order ORD-1001",
        correlation_id="foundry-corr-001",
        simulate_when_ready=True,
    )

    assert result.correlation_id == "foundry-corr-001"
    assert result.status == "foundry_response"
    assert result.message == "Selected tool: getOrderStatus"
    assert result.tool_called is False
    assert result.selected_tool is None
    assert result.planned_action is None
    assert result.simulation_result is None
    assert result.approval_request is None


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
