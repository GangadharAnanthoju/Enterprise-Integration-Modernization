"""Configure durable repositories for the agent application."""

from dataclasses import dataclass

from approvals.requests import (
    AzureTableApprovalRepository,
    InMemoryApprovalRepository,
    set_approval_repository,
)
from audit.events import (
    AzureTableAuditRepository,
    InMemoryAuditRepository,
    set_audit_repository,
)
from config import Settings, get_settings


@dataclass(frozen=True)
class PersistenceConfiguration:
    """Summary of the configured persistence mode."""

    mode: str
    storage_account_url: str | None


def configure_persistence(settings: Settings | None = None) -> PersistenceConfiguration:
    """Configure audit and approval repositories for the selected persistence mode."""

    resolved_settings = settings or get_settings()
    mode = resolved_settings.persistence_mode.lower()
    if mode == "memory":
        set_audit_repository(InMemoryAuditRepository())
        set_approval_repository(InMemoryApprovalRepository())
        return PersistenceConfiguration(mode=mode, storage_account_url=None)

    if mode != "azure_table":
        raise ValueError("PERSISTENCE_MODE must be memory or azure_table.")

    if not resolved_settings.storage_account_url:
        raise ValueError("STORAGE_ACCOUNT_URL is required when PERSISTENCE_MODE=azure_table.")

    from azure.data.tables import TableServiceClient
    from azure.identity import DefaultAzureCredential

    service_client = TableServiceClient(
        endpoint=resolved_settings.storage_account_url,
        credential=DefaultAzureCredential(),
    )
    table_names = (
        resolved_settings.audit_table_name,
        resolved_settings.approval_requests_table_name,
        resolved_settings.approval_decisions_table_name,
    )
    for table_name in table_names:
        service_client.create_table_if_not_exists(table_name)

    set_audit_repository(
        AzureTableAuditRepository(
            service_client.get_table_client(resolved_settings.audit_table_name)
        )
    )
    set_approval_repository(
        AzureTableApprovalRepository(
            service_client.get_table_client(resolved_settings.approval_requests_table_name),
            service_client.get_table_client(resolved_settings.approval_decisions_table_name),
        )
    )
    return PersistenceConfiguration(
        mode=mode,
        storage_account_url=resolved_settings.storage_account_url,
    )
