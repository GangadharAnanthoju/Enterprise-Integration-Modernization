from config import Settings
from foundry.registration_plan import (
    build_foundry_registration_plan,
    run_foundry_registration_preflight,
)


def test_foundry_registration_plan_uses_maf_and_foundry_runtime() -> None:
    plan = build_foundry_registration_plan(
        Settings(
            _env_file=None,
            foundry_project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            model_deployment_name="gpt-4.1-mini",
            foundry_agent_name="enterprise-integration-agent",
        )
    )

    assert plan.agent_name == "enterprise-integration-agent"
    assert plan.display_name == "Enterprise Integration Modernization Agent"
    assert plan.framework == "microsoft_agent_framework"
    assert plan.target_runtime == "microsoft_foundry"
    assert plan.instructions_path == "agent/src/prompts/foundry_agent_instructions.md"
    assert plan.publish_after_registration is False


def test_foundry_registration_preflight_passes_with_configured_foundry_runtime() -> None:
    preflight = run_foundry_registration_preflight(
        Settings(
            _env_file=None,
            foundry_project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            model_deployment_name="gpt-4.1-mini",
            foundry_agent_name="enterprise-integration-agent",
        )
    )

    assert preflight.status == "ready"
    assert preflight.missing == []


def test_foundry_registration_preflight_requires_endpoint_model_and_name_match() -> None:
    preflight = run_foundry_registration_preflight(
        Settings(
            _env_file=None,
            foundry_project_endpoint=None,
            model_deployment_name=None,
            foundry_agent_name="wrong-agent-name",
        )
    )

    assert preflight.status == "needs_attention"
    assert "FOUNDRY_PROJECT_ENDPOINT is required" in preflight.missing
    assert "MODEL_DEPLOYMENT_NAME is required" in preflight.missing
    assert "FOUNDRY_AGENT_NAME must match the local agent definition name" in preflight.missing
