import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_requires_server_only_write_token() -> None:
    with pytest.raises(ValidationError, match="WRITE_API_TOKEN"):
        Settings(environment="production")
    settings = Settings(environment="production", write_api_token="server-secret")
    assert settings.write_api_token is not None
