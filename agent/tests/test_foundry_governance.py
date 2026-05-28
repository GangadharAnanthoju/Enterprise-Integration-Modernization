from foundry.governance import run_readiness_checks


def test_readiness_checks_pass_for_local_governed_agent() -> None:
    report = run_readiness_checks()

    assert report.status == "ready"
    assert {check.name for check in report.checks} == {
        "tool_catalog",
        "high_risk_policy",
        "approval_store",
        "audit_store",
        "observability_projection",
        "mcp_runtime_config",
        "agent_runtime_adapter",
    }
    assert all(check.status == "pass" for check in report.checks)
