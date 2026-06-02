from pathlib import Path

from foundry.agent_definition import (
    load_foundry_agent_definition,
    validate_foundry_agent_definition,
)


AGENT_DEFINITION_PATH = (
    Path(__file__).resolve().parents[2]
    / "foundry"
    / "agent-definitions"
    / "enterprise-integration-agent.yaml"
)


def test_foundry_agent_definition_points_to_instruction_source() -> None:
    definition = AGENT_DEFINITION_PATH.read_text(encoding="utf-8")

    assert "name: enterprise-integration-agent" in definition
    assert "target: microsoft_foundry" in definition
    assert "currentImplementation: local_rule_based_adapter" in definition
    assert "source: agent/src/prompts/foundry_agent_instructions.md" in definition
    assert "executionBoundary: MCP" in definition
    assert "backendImplementation: Logic Apps Standard workflows" in definition


def test_foundry_agent_definition_lists_approved_tool_entries() -> None:
    definition = AGENT_DEFINITION_PATH.read_text(encoding="utf-8")

    assert "name: getOrderStatus" in definition
    assert "name: checkShipmentStatus" in definition
    assert "name: validateInvoice" in definition
    assert "name: queryIntegrationRunStatus" in definition
    assert "name: createApprovalRequest" in definition
    assert "name: sendSupplierNotification" in definition
    assert "name: createServiceNowTicket" in definition
    assert "approvalRequired: true" in definition


def test_foundry_agent_definition_links_governance_boundaries() -> None:
    definition = AGENT_DEFINITION_PATH.read_text(encoding="utf-8")

    assert "toolRegistrySource: agent/src/tools/registry.py" in definition
    assert "riskPolicySource: agent/src/tools/risk_policy.py" in definition
    assert "approvalBoundary: agent/src/approvals/requests.py" in definition
    assert "auditBoundary: agent/src/audit/events.py" in definition
    assert "readinessChecks: agent/src/foundry/governance.py" in definition


def test_foundry_agent_definition_loader_validates_current_skeleton() -> None:
    definition = load_foundry_agent_definition()

    assert definition.name == "enterprise-integration-agent"
    assert definition.instruction_source == "agent/src/prompts/foundry_agent_instructions.md"
    assert definition.instruction_path.exists()
    assert set(definition.approved_tool_names) == {
        "getOrderStatus",
        "checkShipmentStatus",
        "validateInvoice",
        "queryIntegrationRunStatus",
        "createApprovalRequest",
        "sendSupplierNotification",
        "createServiceNowTicket",
    }
    assert validate_foundry_agent_definition(definition) == []
