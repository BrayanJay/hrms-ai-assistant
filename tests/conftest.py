import base64
import json
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch


def _make_jwt(user_id: str = "user-123", username: str = "test.user") -> str:
    """Build a fake JWT whose payload matches what require_user expects."""
    payload = {"data": {"useruuid": user_id, "username": username}}
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    return f"header.{encoded}.signature"


@pytest.fixture
def fake_token() -> str:
    return _make_jwt()


@pytest.fixture
def auth_headers(fake_token: str) -> dict:
    return {"Authorization": f"Bearer {fake_token}"}


@pytest.fixture
def mock_current_user() -> dict:
    return {"sub": "user-123", "username": "test.user"}


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


def _make_llm_response(content: str):
    """Build a minimal object that looks like an OpenAI chat completion response."""
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.fixture
def llm_response_factory():
    return _make_llm_response


@pytest.fixture
async def client():
    from app.main import app
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
