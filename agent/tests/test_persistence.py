from config import Settings
from persistence import configure_persistence


class FakeTableServiceClient:
    created_table_names: list[str] = []

    def __init__(self, *, endpoint: str, credential: object) -> None:
        self.endpoint = endpoint
        self.credential = credential

    def create_table_if_not_exists(self, table_name: str) -> None:
        self.created_table_names.append(table_name)

    def get_table_client(self, table_name: str) -> object:
        return {"table_name": table_name}


class FakeDefaultAzureCredential:
    pass


def test_configure_persistence_uses_memory_by_default() -> None:
    configuration = configure_persistence(Settings(_env_file=None))

    assert configuration.mode == "memory"
    assert configuration.storage_account_url is None


def test_configure_persistence_creates_azure_table_repositories(monkeypatch) -> None:
    FakeTableServiceClient.created_table_names = []
    monkeypatch.setattr("azure.data.tables.TableServiceClient", FakeTableServiceClient)
    monkeypatch.setattr("azure.identity.DefaultAzureCredential", FakeDefaultAzureCredential)

    configuration = configure_persistence(
        Settings(
            _env_file=None,
            persistence_mode="azure_table",
            storage_account_url="https://example.table.core.windows.net",
        )
    )

    assert configuration.mode == "azure_table"
    assert configuration.storage_account_url == "https://example.table.core.windows.net"
    assert FakeTableServiceClient.created_table_names == [
        "AgentAuditEvents",
        "AgentApprovalRequests",
        "AgentApprovalDecisions",
    ]

    configure_persistence(Settings(_env_file=None))
