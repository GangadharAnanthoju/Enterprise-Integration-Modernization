from approvals.requests import (
    AzureTableApprovalRepository,
    InMemoryApprovalRepository,
    create_approval_request,
    decide_approval_request,
    get_approval_decision,
    get_approval_repository,
    get_approval_request,
)


class ResourceNotFoundError(Exception):
    pass


class FakeApprovalTableClient:
    def __init__(self) -> None:
        self.entities: dict[tuple[str, str], dict[str, object]] = {}

    def upsert_entity(self, entity: dict[str, object]) -> None:
        key = (str(entity["PartitionKey"]), str(entity["RowKey"]))
        self.entities[key] = entity

    def get_entity(self, *, partition_key: str, row_key: str) -> dict[str, object]:
        try:
            return self.entities[(partition_key, row_key)]
        except KeyError as exc:
            raise ResourceNotFoundError from exc


def test_in_memory_approval_repository_records_requests_and_decisions() -> None:
    repository = InMemoryApprovalRepository()

    approval_request = repository.create_request(
        correlation_id="approval-repo-corr-001",
        requested_tool="sendSupplierNotification",
        requested_entities={"shipment_id": "SHIP-3001"},
        reason="High-risk enterprise actions require human approval before execution.",
    )
    approval_decision = repository.decide_request(
        approval_id=approval_request.approval_id,
        decision="approved",
        reviewer="integration.manager@contoso.com",
        comment="Approved for supplier communication.",
    )

    assert approval_request.approval_id == "apr-approval-repo-corr-001"
    assert repository.get_request(approval_request.approval_id) == approval_request
    assert approval_decision is not None
    assert approval_decision.approval_id == approval_request.approval_id
    assert approval_decision.correlation_id == approval_request.correlation_id
    assert approval_decision.requested_tool == approval_request.requested_tool
    assert approval_decision.status == "approved"
    assert repository.get_decision(approval_request.approval_id) == approval_decision
    assert repository.is_available() is True


def test_in_memory_approval_repository_returns_none_for_unknown_decision() -> None:
    repository = InMemoryApprovalRepository()

    decision = repository.decide_request(
        approval_id="apr-missing",
        decision="approved",
        reviewer="integration.manager@contoso.com",
        comment=None,
    )

    assert decision is None


def test_approval_module_uses_configured_repository_boundary() -> None:
    approval_request = create_approval_request(
        correlation_id="approval-module-corr-001",
        requested_tool="sendSupplierNotification",
        requested_entities={"shipment_id": "SHIP-3002"},
        reason="High-risk enterprise actions require human approval before execution.",
    )
    approval_decision = decide_approval_request(
        approval_id=approval_request.approval_id,
        decision="rejected",
        reviewer="integration.manager@contoso.com",
        comment="Need more context.",
    )

    assert get_approval_request(approval_request.approval_id) == approval_request
    assert get_approval_decision(approval_request.approval_id) == approval_decision
    assert get_approval_repository().is_available() is True


def test_azure_table_approval_repository_persists_between_instances() -> None:
    requests_table = FakeApprovalTableClient()
    decisions_table = FakeApprovalTableClient()
    writer = AzureTableApprovalRepository(requests_table, decisions_table)

    request = writer.create_request(
        correlation_id="approval-azure-corr-001",
        requested_tool="sendSupplierNotification",
        requested_entities={"shipment_id": "SHIP-3003"},
        reason="High-risk enterprise actions require human approval before execution.",
    )
    decision = writer.decide_request(
        approval_id=request.approval_id,
        decision="approved",
        reviewer="integration.manager@contoso.com",
        comment=None,
    )

    reader = AzureTableApprovalRepository(requests_table, decisions_table)
    assert reader.get_request(request.approval_id) == request
    assert reader.get_decision(request.approval_id) == decision
    assert reader.is_available() is True
