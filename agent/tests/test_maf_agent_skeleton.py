from config import Settings
from foundry.agent_adapter import MafFoundryAgentAdapter
from maf_runtime.enterprise_agent import (
    build_enterprise_maf_agent_skeleton,
    get_maf_package_status,
    validate_enterprise_maf_agent_skeleton,
)


def test_maf_agent_skeleton_loads_instructions_and_runtime_settings() -> None:
    skeleton = build_enterprise_maf_agent_skeleton(
        Settings(
            _env_file=None,
            foundry_project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            model_deployment_name="gpt-4.1-mini",
            foundry_agent_name="enterprise-integration-agent",
        )
    )

    assert skeleton.name == "enterprise-integration-agent"
    assert skeleton.framework == "microsoft_agent_framework"
    assert skeleton.provider == "agent_framework.foundry"
    assert skeleton.model_deployment_name == "gpt-4.1-mini"
    assert skeleton.instructions_path == "agent/src/prompts/foundry_agent_instructions.md"
    assert "approved MCP tools" in skeleton.instructions
    assert skeleton.tool_execution_boundary == "MCP"
    assert skeleton.enterprise_control_plane == "FastAPI"


def test_maf_agent_skeleton_validation_requires_foundry_runtime_settings() -> None:
    missing = validate_enterprise_maf_agent_skeleton(
        Settings(
            _env_file=None,
            foundry_project_endpoint=None,
            model_deployment_name=None,
            foundry_agent_name="enterprise-integration-agent",
        )
    )

    assert "FOUNDRY_PROJECT_ENDPOINT is required" in missing
    assert "MODEL_DEPLOYMENT_NAME is required" in missing


def test_maf_foundry_adapter_metadata_is_live_planning_only() -> None:
    adapter = MafFoundryAgentAdapter()

    assert adapter.name == "enterprise-integration-agent"
    assert adapter.runtime == "microsoft_foundry"
    assert adapter.implementation_status == "live_foundry_invocation_planning_only"


def test_maf_package_status_is_informational() -> None:
    status = get_maf_package_status()

    assert isinstance(status.agent_framework_available, bool)
    assert isinstance(status.foundry_provider_available, bool)
