import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_requires_server_only_write_token() -> None:
    with pytest.raises(ValidationError, match="WRITE_API_TOKEN"):
        Settings(environment="production")
    settings = Settings(environment="production", write_api_token="server-secret")
    assert settings.write_api_token is not None


def test_deployment_list_variables_accept_comma_separated_values(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "https://app.example.test,https://admin.example.test")
    monkeypatch.setenv("TRUSTED_HOSTS", "api.example.test,api")

    settings = Settings()

    assert settings.cors_origins == (
        "https://app.example.test",
        "https://admin.example.test",
    )
    assert settings.trusted_hosts == ("api.example.test", "api")
