from foundry.agent_adapter import get_agent_adapter
from foundry.evaluations import list_evaluation_cases, run_local_evaluation_suite


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
