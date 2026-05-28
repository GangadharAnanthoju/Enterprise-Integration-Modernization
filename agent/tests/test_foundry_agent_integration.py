from foundry.evaluations import list_evaluation_cases, run_local_evaluation_suite


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
