"""Resolve application secrets without exposing them to callers."""

from functools import lru_cache
from typing import Protocol

from config import Settings


class SecretProvider(Protocol):
    """Boundary for retrieving named secrets."""

    def get_secret(self, secret_name: str) -> str | None:
        """Return a secret value or None when it is unavailable."""


class EnvironmentSecretProvider:
    """Use values already loaded into application settings."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def get_secret(self, secret_name: str) -> str | None:
        """Return the configured environment value for a supported secret."""

        if secret_name == self._settings.mcp_api_key_secret_name:
            return _blank_to_none(self._settings.mcp_api_key)
        return None


class KeyVaultSecretProvider:
    """Load secrets from Azure Key Vault using DefaultAzureCredential."""

    def __init__(self, vault_url: str) -> None:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        self._client = SecretClient(
            vault_url=vault_url,
            credential=DefaultAzureCredential(),
        )

    def get_secret(self, secret_name: str) -> str | None:
        """Return one secret value from Azure Key Vault."""

        return _blank_to_none(self._client.get_secret(secret_name).value)


def resolve_mcp_api_key(settings: Settings) -> str | None:
    """Resolve the MCP API key from the configured secret provider."""

    provider = get_secret_provider(
        provider_name=settings.secret_provider,
        key_vault_url=settings.key_vault_url,
        settings=settings,
    )
    return provider.get_secret(settings.mcp_api_key_secret_name)


@lru_cache(maxsize=4)
def _get_key_vault_provider(vault_url: str) -> KeyVaultSecretProvider:
    """Return a cached Key Vault provider so requests reuse its client."""

    return KeyVaultSecretProvider(vault_url)


def get_secret_provider(
    *,
    provider_name: str,
    key_vault_url: str | None,
    settings: Settings,
) -> SecretProvider:
    """Return the selected secret provider."""

    normalized_provider = provider_name.lower()
    if normalized_provider == "environment":
        return EnvironmentSecretProvider(settings)
    if normalized_provider == "key_vault":
        if not key_vault_url:
            raise ValueError("KEY_VAULT_URL is required when SECRET_PROVIDER=key_vault.")
        return _get_key_vault_provider(key_vault_url)
    raise ValueError("SECRET_PROVIDER must be environment or key_vault.")


def _blank_to_none(value: str | None) -> str | None:
    """Treat empty secret values as unset."""

    if value is None:
        return None
    stripped_value = value.strip()
    return stripped_value or None
