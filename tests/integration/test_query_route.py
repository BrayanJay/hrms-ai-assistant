import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.schemas.agent import RouterDecision


# ── Shared fixtures ────────────────────────────────────────────────────────────

def _rag_decision(**overrides) -> RouterDecision:
    return RouterDecision(
        intent="RAG",
        language="en",
        rag_query="annual leave policy",
        tool_name=None,
        tool_params=None,
        is_sequential=False,
        is_write=False,
        chat_response_hint=None,
        **overrides,
    )


def _tool_decision(**overrides) -> RouterDecision:
    return RouterDecision(
        intent="TOOL",
        language="en",
        rag_query=None,
        tool_name="get_leave_balance",
        tool_params={"employee_id": "CURRENT_USER"},
        is_sequential=False,
        is_write=False,
        chat_response_hint=None,
        **overrides,
    )


def _chat_decision(**overrides) -> RouterDecision:
    return RouterDecision(
        intent="CHAT",
        language="en",
        rag_query=None,
        tool_name=None,
        tool_params=None,
        is_sequential=False,
        is_write=False,
        chat_response_hint="Be empathetic.",
        **overrides,
    )


def _make_context_chunk(citation: int = 1) -> dict:
    return {
        "citation": citation,
        "type": "text",
        "content": "Annual leave is 14 days per year.",
        "doc_id": "doc-1",
        "doc_name": "Leave Policy.pdf",
        "page": 1,
    }


# ── Helper to run a query with all external dependencies mocked ───────────────

async def _post_query(
    client: AsyncClient,
    auth_headers: dict,
    query: str = "What is the annual leave policy?",
    session_id: str = "session-abc",
):
    return await client.post(
        "/api/query/",
        json={"session_id": session_id, "query": query},
        headers=auth_headers,
    )


# ── RAG intent tests ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rag_intent_returns_answer_with_citations(client, auth_headers, mock_db):
    from app.main import app
    from app.api.dependencies import require_user
    from app.core.database import get_db

    app.dependency_overrides[require_user] = lambda: {"sub": "user-123", "username": "test.user"}
    app.dependency_overrides[get_db] = lambda: mock_db

    with (
        patch("app.api.routes.query.get_history", AsyncMock(return_value=[])),
        patch("app.api.routes.query.set_history", AsyncMock()),
        patch("app.api.routes.query.compact_history", AsyncMock(side_effect=lambda h: h)),
        patch("app.api.routes.query.classify_intent", AsyncMock(return_value=_rag_decision())),
        patch("app.api.routes.query.to_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.from_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.get_answer", AsyncMock(return_value=None)),
        patch("app.api.routes.query.set_answer", AsyncMock()),
        patch("app.api.routes.query.retrieve", AsyncMock(return_value=[_make_context_chunk()])),
        patch("app.api.routes.query.generate", AsyncMock(return_value="Annual leave is 14 days [1].")),
    ):
        response = await _post_query(client, auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Annual leave is 14 days [1]."
    assert len(body["citations"]) == 1
    assert body["citations"][0]["citation"] == 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_rag_cache_hit_skips_retrieval_and_generation(client, auth_headers, mock_db):
    from app.main import app
    from app.api.dependencies import require_user
    from app.core.database import get_db

    app.dependency_overrides[require_user] = lambda: {"sub": "user-123", "username": "test.user"}
    app.dependency_overrides[get_db] = lambda: mock_db

    cached = {"answer": "Cached answer.", "citations": []}

    with (
        patch("app.api.routes.query.get_history", AsyncMock(return_value=[])),
        patch("app.api.routes.query.set_history", AsyncMock()),
        patch("app.api.routes.query.compact_history", AsyncMock(side_effect=lambda h: h)),
        patch("app.api.routes.query.classify_intent", AsyncMock(return_value=_rag_decision())),
        patch("app.api.routes.query.to_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.from_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.get_answer", AsyncMock(return_value=cached)),
        patch("app.api.routes.query.retrieve") as mock_retrieve,
        patch("app.api.routes.query.generate") as mock_generate,
    ):
        response = await _post_query(client, auth_headers)
        mock_retrieve.assert_not_called()
        mock_generate.assert_not_called()

    assert response.status_code == 200
    assert response.json()["answer"] == "Cached answer."

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_rag_no_context_returns_fallback(client, auth_headers, mock_db):
    from app.main import app
    from app.api.dependencies import require_user
    from app.core.database import get_db

    app.dependency_overrides[require_user] = lambda: {"sub": "user-123", "username": "test.user"}
    app.dependency_overrides[get_db] = lambda: mock_db

    with (
        patch("app.api.routes.query.get_history", AsyncMock(return_value=[])),
        patch("app.api.routes.query.set_history", AsyncMock()),
        patch("app.api.routes.query.compact_history", AsyncMock(side_effect=lambda h: h)),
        patch("app.api.routes.query.classify_intent", AsyncMock(return_value=_rag_decision())),
        patch("app.api.routes.query.to_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.from_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.get_answer", AsyncMock(return_value=None)),
        patch("app.api.routes.query.retrieve", AsyncMock(return_value=[])),
        patch("app.api.routes.query.generate") as mock_generate,
    ):
        response = await _post_query(client, auth_headers)
        mock_generate.assert_not_called()

    assert response.status_code == 200
    assert "don't have enough information" in response.json()["answer"]

    app.dependency_overrides.clear()


# ── TOOL intent tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_tool_intent_returns_generated_answer(client, auth_headers, mock_db):
    from app.main import app
    from app.api.dependencies import require_user
    from app.core.database import get_db

    app.dependency_overrides[require_user] = lambda: {"sub": "user-123", "username": "test.user"}
    app.dependency_overrides[get_db] = lambda: mock_db

    tool_data = {"annual_leave": 14, "sick_leave": 7}

    with (
        patch("app.api.routes.query.get_history", AsyncMock(return_value=[])),
        patch("app.api.routes.query.set_history", AsyncMock()),
        patch("app.api.routes.query.compact_history", AsyncMock(side_effect=lambda h: h)),
        patch("app.api.routes.query.classify_intent", AsyncMock(return_value=_tool_decision())),
        patch("app.api.routes.query.to_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.from_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.execute_tool", AsyncMock(return_value=tool_data)),
        patch("app.api.routes.query.generate", AsyncMock(return_value="Your annual leave balance is 14 days.")),
    ):
        response = await _post_query(client, auth_headers, query="What is my leave balance?")

    assert response.status_code == 200
    assert response.json()["answer"] == "Your annual leave balance is 14 days."
    assert response.json()["requires_confirmation"] is False

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_tool_failure_returns_error_message(client, auth_headers, mock_db):
    from app.main import app
    from app.api.dependencies import require_user
    from app.core.database import get_db
    from app.services.tools.executor import ToolCallError

    app.dependency_overrides[require_user] = lambda: {"sub": "user-123", "username": "test.user"}
    app.dependency_overrides[get_db] = lambda: mock_db

    with (
        patch("app.api.routes.query.get_history", AsyncMock(return_value=[])),
        patch("app.api.routes.query.set_history", AsyncMock()),
        patch("app.api.routes.query.compact_history", AsyncMock(side_effect=lambda h: h)),
        patch("app.api.routes.query.classify_intent", AsyncMock(return_value=_tool_decision())),
        patch("app.api.routes.query.to_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.from_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.execute_tool", AsyncMock(side_effect=ToolCallError("HRIS unreachable"))),
    ):
        response = await _post_query(client, auth_headers, query="What is my leave balance?")

    assert response.status_code == 200
    assert "couldn't retrieve" in response.json()["answer"]

    app.dependency_overrides.clear()


# ── CHAT intent tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_intent_returns_conversational_answer(client, auth_headers, mock_db):
    from app.main import app
    from app.api.dependencies import require_user
    from app.core.database import get_db

    app.dependency_overrides[require_user] = lambda: {"sub": "user-123", "username": "test.user"}
    app.dependency_overrides[get_db] = lambda: mock_db

    with (
        patch("app.api.routes.query.get_history", AsyncMock(return_value=[])),
        patch("app.api.routes.query.set_history", AsyncMock()),
        patch("app.api.routes.query.compact_history", AsyncMock(side_effect=lambda h: h)),
        patch("app.api.routes.query.classify_intent", AsyncMock(return_value=_chat_decision())),
        patch("app.api.routes.query.to_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.from_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.generate", AsyncMock(return_value="I hope you feel better soon!")),
    ):
        response = await _post_query(client, auth_headers, query="I don't feel well today.")

    assert response.status_code == 200
    assert response.json()["answer"] == "I hope you feel better soon!"
    assert response.json()["citations"] == []

    app.dependency_overrides.clear()


# ── Sinhala multilingual tests ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sinhala_query_translated_to_english_before_retrieval(client, auth_headers, mock_db):
    """to_english is called and the translated text is used for retrieval, not the original."""
    from app.main import app
    from app.api.dependencies import require_user
    from app.core.database import get_db

    app.dependency_overrides[require_user] = lambda: {"sub": "user-123", "username": "test.user"}
    app.dependency_overrides[get_db] = lambda: mock_db

    sinhala_query = "මගේ නිවාඩු ශේෂය කොපමනද?"
    english_query = "What is my leave balance?"

    mock_retrieve = AsyncMock(return_value=[_make_context_chunk()])

    with (
        patch("app.api.routes.query.get_history", AsyncMock(return_value=[])),
        patch("app.api.routes.query.set_history", AsyncMock()),
        patch("app.api.routes.query.compact_history", AsyncMock(side_effect=lambda h: h)),
        patch("app.api.routes.query.classify_intent", AsyncMock(return_value=_rag_decision(language="si"))),
        patch("app.api.routes.query.to_english", AsyncMock(return_value=english_query)),
        patch("app.api.routes.query.from_english", AsyncMock(side_effect=lambda t, l: t)),
        patch("app.api.routes.query.get_answer", AsyncMock(return_value=None)),
        patch("app.api.routes.query.set_answer", AsyncMock()),
        patch("app.api.routes.query.retrieve", mock_retrieve),
        patch("app.api.routes.query.generate", AsyncMock(return_value="Your balance is 14 days [1].")),
    ):
        response = await _post_query(client, auth_headers, query=sinhala_query)

    # retrieve was called with the English query, not the Sinhala original
    retrieve_call_query = mock_retrieve.call_args[0][0]
    assert retrieve_call_query == english_query
    assert response.status_code == 200

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sinhala_answer_translated_before_returning(client, auth_headers, mock_db):
    """from_english is called and its output is what the user receives."""
    from app.main import app
    from app.api.dependencies import require_user
    from app.core.database import get_db

    app.dependency_overrides[require_user] = lambda: {"sub": "user-123", "username": "test.user"}
    app.dependency_overrides[get_db] = lambda: mock_db

    sinhala_answer = "ඔබගේ වාර්ෂික නිවාඩු ශේෂය දින 14 කි."

    with (
        patch("app.api.routes.query.get_history", AsyncMock(return_value=[])),
        patch("app.api.routes.query.set_history", AsyncMock()),
        patch("app.api.routes.query.compact_history", AsyncMock(side_effect=lambda h: h)),
        patch("app.api.routes.query.classify_intent", AsyncMock(return_value=_rag_decision(language="si"))),
        patch("app.api.routes.query.to_english", AsyncMock(return_value="What is my leave balance?")),
        patch("app.api.routes.query.from_english", AsyncMock(return_value=sinhala_answer)),
        patch("app.api.routes.query.get_answer", AsyncMock(return_value=None)),
        patch("app.api.routes.query.set_answer", AsyncMock()),
        patch("app.api.routes.query.retrieve", AsyncMock(return_value=[_make_context_chunk()])),
        patch("app.api.routes.query.generate", AsyncMock(return_value="Your annual leave balance is 14 days [1].")),
    ):
        response = await _post_query(client, auth_headers, query="මගේ නිවාඩු ශේෂය කොපමනද?")

    assert response.status_code == 200
    assert response.json()["answer"] == sinhala_answer

    app.dependency_overrides.clear()


# ── Auth tests ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_missing_auth_header_returns_401(client):
    response = await client.post(
        "/api/query/",
        json={"session_id": "s1", "query": "hello"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_returns_401(client):
    response = await client.post(
        "/api/query/",
        json={"session_id": "s1", "query": "hello"},
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert response.status_code == 401
