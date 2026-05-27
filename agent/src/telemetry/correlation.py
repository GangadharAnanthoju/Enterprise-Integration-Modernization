"""Correlation ID helpers."""

from uuid import uuid4


def generate_correlation_id() -> str:
    """Create a new correlation ID for tracing one request across components."""

    return str(uuid4())


def resolve_correlation_id(correlation_id: str | None) -> str:
    """Use the caller-provided correlation ID or create a new one."""

    if correlation_id:
        return correlation_id
    return generate_correlation_id()
