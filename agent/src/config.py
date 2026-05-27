from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "dev"
    agent_name: str = "enterprise-integration-agent"
    foundry_project_endpoint: str | None = None
    model_deployment_name: str | None = None
    foundry_agent_name: str = "enterprise-integration-agent"
    foundry_eval_dataset_name: str = "enterprise-mcp-regression"
    mcp_server_url: str | None = None
    mcp_api_key: str | None = None
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
    )


def get_settings() -> Settings:
    return Settings()
