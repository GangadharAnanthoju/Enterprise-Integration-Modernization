from config import Settings
from config_validation import validate_environment


def test_validate_environment_passes_for_default_mock_mode() -> None:
    report = validate_environment(Settings())

    assert report.status == "ready"
    checks = {check.name: check for check in report.checks}
    assert checks["mcp_mode"].status == "pass"
    assert checks["remote_mcp_endpoint"].status == "skip"
    assert checks["remote_mcp_auth"].status == "skip"
    assert checks["foundry_runtime"].status == "warning"
    assert checks["appinsights"].status == "warning"


def test_validate_environment_passes_for_complete_remote_mcp_settings() -> None:
    report = validate_environment(
        Settings(
            mock_mcp=False,
            mcp_execution_mode="remote",
            mcp_server_url="https://example.contoso/mcp",
            mcp_api_key="secret-token",
            foundry_project_endpoint="https://example.services.ai.azure.com",
            model_deployment_name="gpt-4.1-mini",
            applicationinsights_connection_string="InstrumentationKey=test",
        )
    )

    checks = {check.name: check for check in report.checks}
    assert report.status == "ready"
    assert checks["mcp_mode"].status == "pass"
    assert checks["remote_mcp_endpoint"].status == "pass"
    assert checks["remote_mcp_auth"].status == "pass"
    assert checks["foundry_runtime"].status == "pass"
    assert checks["appinsights"].status == "pass"


def test_validate_environment_fails_for_remote_mode_without_endpoint_or_key() -> None:
    report = validate_environment(
        Settings(
            mock_mcp=False,
            mcp_execution_mode="remote",
            mcp_server_url=None,
            mcp_api_key=None,
        )
    )

    checks = {check.name: check for check in report.checks}
    assert report.status == "needs_attention"
    assert checks["remote_mcp_endpoint"].status == "fail"
    assert checks["remote_mcp_endpoint"].details == "Remote MCP mode requires MCP_SERVER_URL."
    assert checks["remote_mcp_auth"].status == "fail"
    assert checks["remote_mcp_auth"].details == "Remote MCP mode requires MCP_API_KEY."


def test_validate_environment_fails_for_inconsistent_mcp_mode() -> None:
    report = validate_environment(Settings(mock_mcp=True, mcp_execution_mode="remote"))

    checks = {check.name: check for check in report.checks}
    assert report.status == "needs_attention"
    assert checks["mcp_mode"].status == "fail"
