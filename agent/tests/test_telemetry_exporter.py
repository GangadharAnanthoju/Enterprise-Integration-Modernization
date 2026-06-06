import logging

from audit.events import AuditEvent
from config import Settings
from telemetry.exporter import (
    LOGGER_NAME,
    configure_observability,
    emit_audit_event,
)


def test_observability_is_disabled_without_appinsights_connection() -> None:
    configuration = configure_observability(
        Settings(_env_file=None, applicationinsights_connection_string=None)
    )

    assert configuration.enabled is False
    assert configuration.exporter == "disabled"


def test_observability_configures_azure_monitor_with_managed_identity(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    class FakeCredential:
        pass

    monkeypatch.setattr("azure.identity.DefaultAzureCredential", FakeCredential)
    monkeypatch.setattr(
        "azure.monitor.opentelemetry.configure_azure_monitor",
        lambda **kwargs: calls.append(kwargs),
    )

    configuration = configure_observability(
        Settings(
            _env_file=None,
            applicationinsights_connection_string="InstrumentationKey=test",
        )
    )

    assert configuration.enabled is True
    assert configuration.exporter == "azure_monitor_opentelemetry"
    assert calls[0]["connection_string"] == "InstrumentationKey=test"
    assert isinstance(calls[0]["credential"], FakeCredential)
    assert calls[0]["enable_live_metrics"] is False
    assert calls[0]["logger_name"] == LOGGER_NAME


def test_emit_audit_event_writes_query_friendly_dimensions(caplog) -> None:
    event = AuditEvent(
        event_id="audit-observe-001",
        correlation_id="corr-observe-001",
        event_type="tool_simulation_completed",
        source="agent.chat",
        status="completed",
        details={
            "tool_name": "getOrderStatus",
            "risk_decision": "allow",
            "mode": "remote",
            "request_payload": {"order_id": "ORD-1001"},
        },
    )

    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        emit_audit_event(event)

    record = caplog.records[-1]
    assert record.message == "enterprise.integration.tool_simulation_completed"
    assert record.correlation_id == "corr-observe-001"
    assert record.tool_name == "getOrderStatus"
    assert record.risk_decision == "allow"
    assert record.mode == "remote"
    assert '"order_id":"ORD-1001"' in record.details_json
