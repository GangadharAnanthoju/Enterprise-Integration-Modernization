from config import Settings
import pytest
from foundry.live_agent import (
    FoundryAgentRegistrationError,
    build_prompt_agent_definition,
    create_or_update_foundry_prompt_agent_version,
    invoke_foundry_agent_message,
)


class FakeAgentVersionResponse:
    def as_dict(self) -> dict[str, object]:
        return {
            "version": "1",
            "status": "succeeded",
            "name": "enterprise-integration-agent",
        }


class FakeAgentsOperations:
    def __init__(self) -> None:
        self.created_agent_name: str | None = None
        self.created_definition = None
        self.created_metadata = None
        self.created_description: str | None = None

    def create_version(self, agent_name, *, definition, metadata, description):
        self.created_agent_name = agent_name
        self.created_definition = definition
        self.created_metadata = metadata
        self.created_description = description
        return FakeAgentVersionResponse()


class FakeProjectClient:
    def __init__(self) -> None:
        self.agents = FakeAgentsOperations()


class FakeAgentRunResponse:
    text = "I would use the approved getOrderStatus MCP tool for ORD-1001."
    response_id = "resp-123"

    def to_dict(self) -> dict[str, object]:
        return {
            "response_id": self.response_id,
            "messages": [{"role": "assistant", "content": self.text}],
        }


class FakeRuntimeAgent:
    def __init__(self) -> None:
        self.received_message: str | None = None

    async def run(self, message: str) -> FakeAgentRunResponse:
        self.received_message = message
        return FakeAgentRunResponse()


def test_build_prompt_agent_definition_uses_model_and_instruction_file() -> None:
    definition = build_prompt_agent_definition(
        Settings(
            _env_file=None,
            model_deployment_name="gpt-4.1-mini",
        )
    )

    body = definition.as_dict()
    assert body["kind"] == "prompt"
    assert body["model"] == "gpt-4.1-mini"
    assert "approved MCP tools" in body["instructions"]
    assert body["temperature"] == 0.2


def test_create_or_update_foundry_prompt_agent_version_uses_project_client() -> None:
    fake_client = FakeProjectClient()

    result = create_or_update_foundry_prompt_agent_version(
        Settings(
            _env_file=None,
            foundry_project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            model_deployment_name="gpt-4.1-mini",
            foundry_agent_name="enterprise-integration-agent",
        ),
        project_client=fake_client,
    )

    assert fake_client.agents.created_agent_name == "enterprise-integration-agent"
    assert fake_client.agents.created_definition.as_dict()["model"] == "gpt-4.1-mini"
    assert fake_client.agents.created_metadata["framework"] == "microsoft_agent_framework"
    assert result.agent_name == "enterprise-integration-agent"
    assert result.version == "1"
    assert result.status == "succeeded"


def test_create_or_update_foundry_prompt_agent_version_blocks_failed_preflight() -> None:
    try:
        create_or_update_foundry_prompt_agent_version(
            Settings(
                _env_file=None,
                foundry_project_endpoint=None,
                model_deployment_name=None,
                foundry_agent_name="enterprise-integration-agent",
            ),
            project_client=FakeProjectClient(),
        )
    except FoundryAgentRegistrationError as exc:
        assert "FOUNDRY_PROJECT_ENDPOINT is required" in str(exc)
        assert "MODEL_DEPLOYMENT_NAME is required" in str(exc)
    else:
        raise AssertionError("Live registration must not run when preflight fails.")


def test_invoke_foundry_agent_message_uses_runtime_agent() -> None:
    fake_agent = FakeRuntimeAgent()

    result = invoke_foundry_agent_message(
        "Check order ORD-1001",
        Settings(
            _env_file=None,
            foundry_project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            model_deployment_name="gpt-4.1-mini",
            foundry_agent_name="enterprise-integration-agent",
            foundry_agent_version="1",
        ),
        runtime_agent=fake_agent,
    )

    assert fake_agent.received_message == "Check order ORD-1001"
    assert result.agent_name == "enterprise-integration-agent"
    assert result.agent_version == "1"
    assert result.response_id == "resp-123"
    assert "getOrderStatus" in result.response_text


@pytest.mark.asyncio
async def test_invoke_foundry_agent_message_can_run_inside_existing_event_loop() -> None:
    fake_agent = FakeRuntimeAgent()

    result = invoke_foundry_agent_message(
        "Check order ORD-1001",
        Settings(
            _env_file=None,
            foundry_project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            model_deployment_name="gpt-4.1-mini",
            foundry_agent_name="enterprise-integration-agent",
            foundry_agent_version="1",
        ),
        runtime_agent=fake_agent,
    )

    assert fake_agent.received_message == "Check order ORD-1001"
    assert result.response_id == "resp-123"
