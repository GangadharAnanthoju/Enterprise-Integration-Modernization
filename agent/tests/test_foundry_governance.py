from config import Settings
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
        "environment_validation",
    }
    assert all(check.status == "pass" for check in report.checks)


def test_readiness_checks_fail_when_remote_environment_is_incomplete() -> None:
    report = run_readiness_checks(
        Settings(
            mock_mcp=False,
            mcp_execution_mode="remote",
            mcp_server_url=None,
            mcp_api_key=None,
        )
    )

    checks = {check.name: check for check in report.checks}
    assert report.status == "needs_attention"
    assert checks["mcp_runtime_config"].status == "fail"
    assert checks["environment_validation"].status == "fail"
    assert "remote_mcp_endpoint" in checks["environment_validation"].details
    assert "remote_mcp_auth" in checks["environment_validation"].details
