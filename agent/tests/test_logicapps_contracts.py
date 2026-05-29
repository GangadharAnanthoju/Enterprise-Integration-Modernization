import json
from pathlib import Path

from tools.registry import require_tool


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_get_order_status_logic_app_contract_matches_tool_registry() -> None:
    tool = require_tool("getOrderStatus")
    contract_path = REPO_ROOT / "logicapps/workflows/getOrderStatus/contract.json"

    contract = json.loads(contract_path.read_text(encoding="utf-8"))

    assert contract["tool_name"] == tool.name
    assert contract["workflow_name"] == "getOrderStatus"
    assert contract["risk_level"] == tool.risk_level.value
    assert contract["approval_required"] == tool.approval_required
    assert tuple(contract["required_entities"]) == tool.required_entities
    assert contract["method"] == "POST"


def test_get_order_status_sample_request_matches_required_entities() -> None:
    sample_path = REPO_ROOT / "logicapps/workflows/getOrderStatus/sample-request.json"
    sample_request = json.loads(sample_path.read_text(encoding="utf-8"))

    assert sample_request == {"order_id": "ORD-1001"}


def test_get_order_status_workflow_has_local_logic_app_design() -> None:
    workflow_path = REPO_ROOT / "logicapps/workflows/getOrderStatus/workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))

    definition = workflow["definition"]
    trigger = definition["triggers"]["When_an_HTTP_request_is_received"]
    validation_action = definition["actions"]["Validate_order_id"]
    success_actions = validation_action["actions"]
    failure_actions = validation_action["else"]["actions"]

    assert workflow["kind"] == "Stateful"
    assert trigger["type"] == "Request"
    assert trigger["kind"] == "Http"
    assert trigger["inputs"]["schema"]["required"] == ["order_id"]
    assert validation_action["type"] == "If"
    assert "Compose_order_status_response" in success_actions
    assert success_actions["Return_order_status"]["inputs"]["statusCode"] == 200
    assert failure_actions["Return_missing_order_id"]["inputs"]["statusCode"] == 400


def test_logic_apps_standard_project_copy_matches_get_order_status_workflow() -> None:
    source_path = REPO_ROOT / "logicapps/workflows/getOrderStatus/workflow.json"
    project_path = REPO_ROOT / "logicapps/standard-app/getOrderStatus/workflow.json"

    source_workflow = json.loads(source_path.read_text(encoding="utf-8"))
    project_workflow = json.loads(project_path.read_text(encoding="utf-8"))

    assert project_workflow == source_workflow


def test_logic_apps_standard_workspace_and_sample_request_are_valid() -> None:
    workspace_path = (
        REPO_ROOT
        / "logicapps/standard-app/Enterprise-Integration-LogicApps.code-workspace"
    )
    sample_path = REPO_ROOT / "logicapps/standard-app/getOrderStatus/sample-request.json"

    workspace = json.loads(workspace_path.read_text(encoding="utf-8"))
    sample_request = json.loads(sample_path.read_text(encoding="utf-8"))

    assert workspace["folders"] == [
        {
            "name": "Enterprise Integration Logic Apps",
            "path": ".",
        }
    ]
    assert sample_request == {"order_id": "ORD-1001"}
