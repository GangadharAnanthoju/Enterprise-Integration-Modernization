from config import Settings
from secret_store import (
    EnvironmentSecretProvider,
    get_secret_provider,
    resolve_mcp_api_key,
)


class FakeKeyVaultProvider:
    def get_secret(self, secret_name: str) -> str | None:
        assert secret_name == "logic-apps-mcp-api-key"
        return "key-vault-secret"


def test_environment_secret_provider_returns_mcp_api_key() -> None:
    settings = Settings(_env_file=None, mcp_api_key="environment-secret")
    provider = EnvironmentSecretProvider(settings)

    assert provider.get_secret("logic-apps-mcp-api-key") == "environment-secret"
    assert resolve_mcp_api_key(settings) == "environment-secret"


def test_resolve_mcp_api_key_uses_key_vault_provider(monkeypatch) -> None:
    settings = Settings(
        _env_file=None,
        secret_provider="key_vault",
        key_vault_url="https://example.vault.azure.net/",
        mcp_api_key=None,
    )
    monkeypatch.setattr(
        "secret_store.get_secret_provider",
        lambda **_: FakeKeyVaultProvider(),
    )

    assert resolve_mcp_api_key(settings) == "key-vault-secret"


def test_key_vault_provider_requires_vault_url() -> None:
    settings = Settings(_env_file=None, secret_provider="key_vault", key_vault_url=None)

    try:
        get_secret_provider(
            provider_name=settings.secret_provider,
            key_vault_url=settings.key_vault_url,
            settings=settings,
        )
    except ValueError as exc:
        assert str(exc) == "KEY_VAULT_URL is required when SECRET_PROVIDER=key_vault."
    else:
        raise AssertionError("Key Vault provider must require a vault URL.")
