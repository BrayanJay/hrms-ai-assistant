import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_translation_response(translated_text: str):
    choice = MagicMock()
    choice.message.content = translated_text
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.mark.asyncio
async def test_to_english_sinhala_query():
    """Sinhala query is translated to English via GPT-4o."""
    from app.services.generation.translator import to_english

    mock_response = _make_translation_response("What is my leave balance?")

    with patch("app.services.generation.translator._translation_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        result = await to_english("මගේ නිවාඩු ශේෂය කොපමනද?", "si")

    assert result == "What is my leave balance?"


@pytest.mark.asyncio
async def test_to_english_tamil_query():
    """Tamil query is translated to English via GPT-4o."""
    from app.services.generation.translator import to_english

    mock_response = _make_translation_response("What is the maternity leave policy?")

    with patch("app.services.generation.translator._translation_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        result = await to_english("மகப்பேறு விடுப்பு கொள்கை என்ன?", "ta")

    assert result == "What is the maternity leave policy?"


@pytest.mark.asyncio
async def test_to_english_english_passthrough():
    """English queries bypass translation entirely — no API call made."""
    from app.services.generation.translator import to_english

    with patch("app.services.generation.translator._translation_client") as mock_client:
        result = await to_english("What is my leave balance?", "en")
        mock_client.chat.completions.create.assert_not_called()

    assert result == "What is my leave balance?"


@pytest.mark.asyncio
async def test_to_english_unknown_language_passthrough():
    """Unknown language codes pass the text through unchanged."""
    from app.services.generation.translator import to_english

    with patch("app.services.generation.translator._translation_client") as mock_client:
        result = await to_english("Bonjour", "fr")
        mock_client.chat.completions.create.assert_not_called()

    assert result == "Bonjour"


@pytest.mark.asyncio
async def test_to_english_api_failure_returns_original():
    """If the OpenAI call fails, the original text is returned (graceful fallback)."""
    from app.services.generation.translator import to_english

    with patch("app.services.generation.translator._translation_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("network error"))
        result = await to_english("මගේ නිවාඩු ශේෂය කොපමනද?", "si")

    assert result == "මගේ නිවාඩු ශේෂය කොපමනද?"


@pytest.mark.asyncio
async def test_from_english_to_sinhala():
    """English answer is translated to Sinhala with Markdown preserved."""
    from app.services.generation.translator import from_english

    sinhala_answer = "ඔබගේ **වාර්ෂික නිවාඩු** ශේෂය **දින 14** කි."
    mock_response = _make_translation_response(sinhala_answer)

    with patch("app.services.generation.translator._translation_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        result = await from_english("Your **Annual Leave** balance is **14 days**.", "si")

    assert result == sinhala_answer


@pytest.mark.asyncio
async def test_from_english_to_tamil():
    """English answer is translated to Tamil."""
    from app.services.generation.translator import from_english

    tamil_answer = "உங்கள் **ஆண்டு விடுப்பு** இருப்பு **14 நாட்கள்**."
    mock_response = _make_translation_response(tamil_answer)

    with patch("app.services.generation.translator._translation_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        result = await from_english("Your **Annual Leave** balance is **14 days**.", "ta")

    assert result == tamil_answer


@pytest.mark.asyncio
async def test_from_english_english_passthrough():
    """English target language skips translation — no API call made."""
    from app.services.generation.translator import from_english

    with patch("app.services.generation.translator._translation_client") as mock_client:
        result = await from_english("Your leave balance is 14 days.", "en")
        mock_client.chat.completions.create.assert_not_called()

    assert result == "Your leave balance is 14 days."


@pytest.mark.asyncio
async def test_from_english_api_failure_returns_english():
    """If translation fails, the original English text is returned rather than raising."""
    from app.services.generation.translator import from_english

    with patch("app.services.generation.translator._translation_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("timeout"))
        result = await from_english("Your leave balance is 14 days.", "si")

    assert result == "Your leave balance is 14 days."
