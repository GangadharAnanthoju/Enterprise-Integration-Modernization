from telemetry.correlation import generate_correlation_id, resolve_correlation_id


def test_generate_correlation_id_returns_unique_values() -> None:
    first = generate_correlation_id()
    second = generate_correlation_id()

    assert first
    assert second
    assert first != second


def test_resolve_correlation_id_uses_existing_value() -> None:
    assert resolve_correlation_id("demo-corr-001") == "demo-corr-001"


def test_resolve_correlation_id_generates_missing_value() -> None:
    assert resolve_correlation_id(None)
