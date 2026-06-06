from audit.events import (
    AzureTableAuditRepository,
    InMemoryAuditRepository,
    get_audit_repository,
    list_audit_events,
    record_audit_event,
)


class FakeAuditTableClient:
    def __init__(self) -> None:
        self.entities: list[dict[str, object]] = []

    def create_entity(self, entity: dict[str, object]) -> None:
        self.entities.append(entity)

    def query_entities(self, *, query_filter: str) -> list[dict[str, object]]:
        partition_key = query_filter.removeprefix("PartitionKey eq '").removesuffix("'")
        return [
            entity for entity in self.entities if entity["PartitionKey"] == partition_key
        ]


def test_in_memory_audit_repository_records_events_by_correlation_id() -> None:
    repository = InMemoryAuditRepository()

    first = repository.record(
        correlation_id="audit-repo-corr-001",
        event_type="agent_chat_planned",
        source="test",
        status="completed",
        details={"selected_tool": "getOrderStatus"},
    )
    second = repository.record(
        correlation_id="audit-repo-corr-001",
        event_type="tool_execution_completed",
        source="test",
        status="completed",
        details={"tool_name": "getOrderStatus"},
    )
    repository.record(
        correlation_id="audit-repo-corr-002",
        event_type="agent_chat_planned",
        source="test",
        status="completed",
        details={},
    )

    assert first.event_id == "audit-0001"
    assert second.event_id == "audit-0002"
    assert repository.list_by_correlation_id("audit-repo-corr-001") == [first, second]
    assert repository.is_available() is True


def test_audit_module_uses_configured_repository_boundary() -> None:
    event = record_audit_event(
        correlation_id="audit-module-corr-001",
        event_type="agent_chat_planned",
        source="test",
        status="completed",
        details={"selected_tool": "getOrderStatus"},
    )

    assert event in list_audit_events("audit-module-corr-001")
    assert get_audit_repository().is_available() is True


def test_azure_table_audit_repository_persists_between_instances() -> None:
    table_client = FakeAuditTableClient()
    writer = AzureTableAuditRepository(table_client)

    event = writer.record(
        correlation_id="audit-azure-corr-001",
        event_type="agent_chat_planned",
        source="test",
        status="completed",
        details={"selected_tool": "getOrderStatus"},
    )

    reader = AzureTableAuditRepository(table_client)
    assert reader.list_by_correlation_id("audit-azure-corr-001") == [event]
    assert reader.is_available() is True
