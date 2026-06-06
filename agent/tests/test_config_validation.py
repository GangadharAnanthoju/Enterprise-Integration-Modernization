from config import Settings
from config_validation import validate_environment


def test_validate_environment_passes_for_default_mock_mode() -> None:
    report = validate_environment(Settings(_env_file=None))

    assert report.status == "ready"
    checks = {check.name: check for check in report.checks}
    assert checks["agent_runtime_mode"].status == "pass"
    assert checks["mcp_mode"].status == "pass"
    assert checks["remote_mcp_endpoint"].status == "skip"
    assert checks["remote_mcp_auth"].status == "skip"
    assert checks["foundry_runtime"].status == "warning"
    assert checks["foundry_resource_context"].status == "warning"
    assert checks["secret_provider"].status == "pass"
    assert checks["persistence"].status == "pass"
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
            azure_tenant_id="tenant-id",
            azure_subscription_id="subscription-id",
            azure_resource_group="rg-sysint-ms-foundry",
            azure_ai_account_name="ms-foundry-sysint-02",
            azure_ai_project_name="proj-sysint-01",
            applicationinsights_connection_string="InstrumentationKey=test",
        )
    )

    checks = {check.name: check for check in report.checks}
    assert report.status == "ready"
    assert checks["agent_runtime_mode"].status == "pass"
    assert checks["mcp_mode"].status == "pass"
    assert checks["remote_mcp_endpoint"].status == "pass"
    assert checks["remote_mcp_auth"].status == "pass"
    assert checks["foundry_runtime"].status == "pass"
    assert checks["foundry_resource_context"].status == "pass"
    assert checks["secret_provider"].status == "pass"
    assert checks["persistence"].status == "pass"
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
    assert (
        checks["remote_mcp_endpoint"].details
        == "Remote MCP mode requires MCP_SERVER_URL or at least one per-tool endpoint."
    )
    assert checks["remote_mcp_auth"].status == "fail"
    assert (
        checks["remote_mcp_auth"].details
        == "Remote MCP mode requires MCP_API_KEY or a configured Key Vault provider."
    )


def test_validate_environment_fails_for_inconsistent_mcp_mode() -> None:
    report = validate_environment(
        Settings(_env_file=None, mock_mcp=True, mcp_execution_mode="remote")
    )

    checks = {check.name: check for check in report.checks}
    assert report.status == "needs_attention"
    assert checks["mcp_mode"].status == "fail"


def test_validate_environment_fails_for_unknown_agent_runtime_mode() -> None:
    report = validate_environment(Settings(_env_file=None, agent_runtime_mode="portal"))

    checks = {check.name: check for check in report.checks}
    assert report.status == "needs_attention"
    assert checks["agent_runtime_mode"].status == "fail"
    assert checks["agent_runtime_mode"].details == "AGENT_RUNTIME_MODE must be local or foundry."


def test_validate_environment_allows_local_logic_app_tool_endpoint_without_api_key() -> None:
    report = validate_environment(
        Settings(
            mock_mcp=False,
            mcp_execution_mode="remote",
            mcp_tool_endpoint_get_order_status="http://localhost:7071/api/getOrderStatus",
            mcp_api_key=None,
        )
    )

    checks = {check.name: check for check in report.checks}
    assert report.status == "ready"
    assert checks["remote_mcp_endpoint"].status == "pass"
    assert checks["remote_mcp_auth"].status == "warning"


def test_validate_environment_fails_for_azure_table_mode_without_account_url() -> None:
    report = validate_environment(
        Settings(_env_file=None, persistence_mode="azure_table", storage_account_url=None)
    )

    checks = {check.name: check for check in report.checks}
    assert report.status == "needs_attention"
    assert checks["persistence"].status == "fail"
    assert checks["persistence"].details == "Azure Table persistence requires STORAGE_ACCOUNT_URL."


def test_validate_environment_passes_for_azure_table_mode_with_account_url() -> None:
    report = validate_environment(
        Settings(
            _env_file=None,
            persistence_mode="azure_table",
            storage_account_url="https://stsysintintegeus001.table.core.windows.net",
        )
    )

    checks = {check.name: check for check in report.checks}
    assert checks["persistence"].status == "pass"


def test_validate_environment_passes_for_key_vault_remote_mcp_auth() -> None:
    report = validate_environment(
        Settings(
            _env_file=None,
            mock_mcp=False,
            mcp_execution_mode="remote",
            mcp_server_url="https://example.contoso/mcp",
            mcp_api_key=None,
            secret_provider="key_vault",
            key_vault_url="https://kv-sysint-common-eus.vault.azure.net/",
        )
    )

    checks = {check.name: check for check in report.checks}
    assert checks["remote_mcp_auth"].status == "pass"
    assert checks["secret_provider"].status == "pass"


def test_validate_environment_fails_for_key_vault_without_url() -> None:
    report = validate_environment(
        Settings(_env_file=None, secret_provider="key_vault", key_vault_url=None)
    )

    checks = {check.name: check for check in report.checks}
    assert report.status == "needs_attention"
    assert checks["secret_provider"].status == "fail"
