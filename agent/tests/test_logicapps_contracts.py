import json
from pathlib import Path

from tools.registry import list_tools, require_tool


REPO_ROOT = Path(__file__).resolve().parents[2]


def _contains_response_action(actions: dict[str, object]) -> bool:
    for action in actions.values():
        if not isinstance(action, dict):
            continue
        if action.get("type") == "Response":
            return True
        nested_actions = action.get("actions")
        if isinstance(nested_actions, dict) and _contains_response_action(nested_actions):
            return True
        else_branch = action.get("else")
        if isinstance(else_branch, dict):
            else_actions = else_branch.get("actions")
            if isinstance(else_actions, dict) and _contains_response_action(else_actions):
                return True

    return False


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


def test_all_logic_app_contracts_match_tool_registry() -> None:
    for tool in list_tools():
        contract_path = REPO_ROOT / f"logicapps/workflows/{tool.name}/contract.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))

        assert contract["tool_name"] == tool.name
        assert contract["workflow_name"] == tool.name
        assert contract["risk_level"] == tool.risk_level.value
        assert contract["approval_required"] == tool.approval_required
        assert tuple(contract["required_entities"]) == tool.required_entities
        assert contract["method"] == "POST"


def test_all_logic_app_sample_requests_contain_required_entities() -> None:
    for tool in list_tools():
        sample_path = REPO_ROOT / f"logicapps/workflows/{tool.name}/sample-request.json"
        sample_request = json.loads(sample_path.read_text(encoding="utf-8"))

        assert sample_request["tool_name"] == tool.name
        assert isinstance(sample_request["payload"], dict)
        for required_entity in tool.required_entities:
            assert required_entity in sample_request["payload"]


def test_get_order_status_sample_request_matches_required_entities() -> None:
    sample_path = REPO_ROOT / "logicapps/workflows/getOrderStatus/sample-request.json"
    sample_request = json.loads(sample_path.read_text(encoding="utf-8"))

    assert sample_request["tool_name"] == "getOrderStatus"
    assert sample_request["payload"] == {"order_id": "ORD-1001"}


def test_get_order_status_workflow_has_local_logic_app_design() -> None:
    workflow_path = REPO_ROOT / "logicapps/workflows/getOrderStatus/workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))

    definition = workflow["definition"]
    trigger = definition["triggers"]["When_an_HTTP_request_is_received"]
    validation_action = definition["actions"]["Validate_mcp_envelope"]
    success_actions = validation_action["actions"]
    failure_actions = validation_action["else"]["actions"]

    assert workflow["kind"] == "Stateful"
    assert trigger["type"] == "Request"
    assert trigger["kind"] == "Http"
    assert trigger["inputs"]["schema"]["required"] == [
        "server_name",
        "tool_name",
        "correlation_id",
        "payload",
    ]
    assert validation_action["type"] == "If"
    assert "Compose_order_status_result" in success_actions
    assert success_actions["Return_mcp_order_status"]["inputs"]["statusCode"] == 200
    assert failure_actions["Return_invalid_mcp_request"]["inputs"]["statusCode"] == 400


def test_logic_apps_standard_project_copy_matches_get_order_status_workflow() -> None:
    source_path = REPO_ROOT / "logicapps/workflows/getOrderStatus/workflow.json"
    project_path = REPO_ROOT / "logicapps/standard-app/getOrderStatus/workflow.json"

    source_workflow = json.loads(source_path.read_text(encoding="utf-8"))
    project_workflow = json.loads(project_path.read_text(encoding="utf-8"))

    assert project_workflow == source_workflow


def test_logic_apps_standard_project_contains_every_workflow_copy() -> None:
    for tool in list_tools():
        source_path = REPO_ROOT / f"logicapps/workflows/{tool.name}/workflow.json"
        project_path = REPO_ROOT / f"logicapps/standard-app/{tool.name}/workflow.json"
        source_request_path = REPO_ROOT / f"logicapps/workflows/{tool.name}/sample-request.json"
        project_request_path = REPO_ROOT / f"logicapps/standard-app/{tool.name}/sample-request.json"

        source_workflow = json.loads(source_path.read_text(encoding="utf-8"))
        project_workflow = json.loads(project_path.read_text(encoding="utf-8"))
        source_request = json.loads(source_request_path.read_text(encoding="utf-8"))
        project_request = json.loads(project_request_path.read_text(encoding="utf-8"))

        assert project_workflow == source_workflow
        assert project_request == source_request


def test_all_logic_app_workflows_have_http_trigger_and_response_action() -> None:
    for tool in list_tools():
        workflow_path = REPO_ROOT / f"logicapps/workflows/{tool.name}/workflow.json"
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
        definition = workflow["definition"]
        trigger = definition["triggers"]["When_an_HTTP_request_is_received"]
        actions = definition["actions"]

        assert workflow["kind"] == "Stateful"
        assert trigger["type"] == "Request"
        assert trigger["kind"] == "Http"
        assert actions
        assert _contains_response_action(actions)


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
    assert sample_request["tool_name"] == "getOrderStatus"
    assert sample_request["payload"] == {"order_id": "ORD-1001"}
