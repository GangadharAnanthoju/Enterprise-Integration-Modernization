from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "dev"
    agent_name: str = "enterprise-integration-agent"
    foundry_project_endpoint: str | None = None
    model_deployment_name: str | None = None
    foundry_agent_name: str = "enterprise-integration-agent"
    foundry_eval_dataset_name: str = "enterprise-mcp-regression"
    azure_subscription_id: str | None = None
    azure_resource_group: str | None = None
    azure_ai_account_name: str | None = None
    azure_ai_project_name: str | None = None
    mcp_execution_mode: str = "mock"
    mcp_server_name: str = "logic-apps-standard-mcp"
    mcp_server_url: str | None = None
    mcp_tool_endpoint_get_order_status: str | None = None
    mcp_tool_endpoint_check_shipment_status: str | None = None
    mcp_tool_endpoint_validate_invoice: str | None = None
    mcp_tool_endpoint_query_integration_run_status: str | None = None
    mcp_tool_endpoint_create_approval_request: str | None = None
    mcp_tool_endpoint_create_servicenow_ticket: str | None = None
    mcp_tool_endpoint_send_supplier_notification: str | None = None
    mcp_api_key: str | None = None
    mcp_timeout_seconds: int = 30
    mock_mcp: bool = True
    applicationinsights_connection_string: str | None = None
    azure_tenant_id: str | None = None
    azure_client_id: str | None = None
    key_vault_url: str | None = None
    service_bus_namespace: str | None = None
    log_analytics_workspace_id: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )


def get_settings() -> Settings:
    return Settings()
