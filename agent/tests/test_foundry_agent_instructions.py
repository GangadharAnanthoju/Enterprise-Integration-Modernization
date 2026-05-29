from pathlib import Path


INSTRUCTIONS_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "prompts"
    / "foundry_agent_instructions.md"
)


def test_foundry_agent_instructions_capture_governance_rules() -> None:
    instructions = INSTRUCTIONS_PATH.read_text(encoding="utf-8").lower()

    assert "approved mcp tools" in instructions
    assert "never invent tool names" in instructions
    assert "treat mcp as the only backend execution path" in instructions
    assert "high-risk tools must not execute directly from chat" in instructions
    assert "approval is recorded" in instructions
    assert "correlation id" in instructions


def test_foundry_agent_instructions_name_current_tool_examples() -> None:
    instructions = INSTRUCTIONS_PATH.read_text(encoding="utf-8")

    assert "`getOrderStatus`" in instructions
    assert "`checkShipmentStatus`" in instructions
    assert "`validateInvoice`" in instructions
    assert "`queryIntegrationRunStatus`" in instructions
    assert "`sendSupplierNotification`" in instructions
    assert "`createServiceNowTicket`" in instructions
