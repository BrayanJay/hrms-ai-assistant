import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_llm_response(content: str):
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


def _make_history(num_turns: int, chars_per_message: int = 100) -> list[dict]:
    """Generate alternating user/assistant messages of a given character length."""
    history = []
    for i in range(num_turns):
        role = "user" if i % 2 == 0 else "assistant"
        history.append({"role": role, "content": "x" * chars_per_message})
    return history


@pytest.mark.asyncio
async def test_compact_history_below_threshold_returns_unchanged():
    """History under the char threshold is returned as-is without calling the LLM."""
    from app.services.generation.summarizer import compact_history

    history = _make_history(num_turns=4, chars_per_message=100)  # 400 chars, well under 8000

    with patch("app.services.generation.summarizer.llm_client") as mock_client:
        result = await compact_history(history)
        mock_client.chat.completions.create.assert_not_called()

    assert result == history


@pytest.mark.asyncio
async def test_compact_history_too_few_turns_returns_unchanged():
    """History that exceeds threshold but has <= keep_recent turns is never compacted."""
    from app.services.generation.summarizer import compact_history

    # 6 messages each 2000 chars = 12000 chars — over threshold
    # but len(history) == 6 == history_keep_recent, so no compaction
    history = _make_history(num_turns=6, chars_per_message=2000)

    with patch("app.services.generation.summarizer.llm_client") as mock_client:
        result = await compact_history(history)
        mock_client.chat.completions.create.assert_not_called()

    assert result == history


@pytest.mark.asyncio
async def test_compact_history_compacts_when_over_threshold():
    """History over threshold with enough turns is summarized; recent turns are kept."""
    from app.services.generation.summarizer import compact_history

    # 10 messages × 1000 chars = 10000 chars — over threshold (8000)
    history = _make_history(num_turns=10, chars_per_message=1000)
    summary_text = "The employee asked about leave balances and received details."

    with patch("app.services.generation.summarizer.llm_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(
            return_value=_make_llm_response(summary_text)
        )
        result = await compact_history(history)

    # Result: 2 synthetic messages + last 6 turns = 8 messages
    assert len(result) == 8
    assert result[0]["role"] == "user"
    assert "[Earlier conversation summary]" in result[0]["content"]
    assert summary_text in result[0]["content"]
    assert result[1]["role"] == "assistant"
    # Last 6 turns of original history are preserved
    assert result[2:] == history[-6:]


@pytest.mark.asyncio
async def test_compact_history_llm_called_with_old_turns_only():
    """The LLM summarizer receives only the old turns, not the recent ones."""
    from app.services.generation.summarizer import compact_history

    history = _make_history(num_turns=10, chars_per_message=1000)
    old_turns = history[:-6]  # first 4 turns

    with patch("app.services.generation.summarizer.llm_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(
            return_value=_make_llm_response("summary")
        )
        await compact_history(history)

    call_args = mock_client.chat.completions.create.call_args
    messages_sent = call_args.kwargs["messages"]

    # The user message (index 1) should contain only the old turns in the transcript
    transcript = messages_sent[1]["content"]
    for turn in old_turns:
        assert turn["content"] in transcript

    # Recent turns should NOT be in the transcript sent to the LLM
    for turn in history[-6:]:
        assert turn["content"] not in transcript


@pytest.mark.asyncio
async def test_compact_history_uses_qwen_not_openai():
    """Summarizer uses llm_client (vLLM/Qwen3), not the OpenAI translation client."""
    from app.services.generation.summarizer import compact_history

    history = _make_history(num_turns=10, chars_per_message=1000)

    with patch("app.services.generation.summarizer.llm_client") as mock_llm:
        mock_llm.chat.completions.create = AsyncMock(
            return_value=_make_llm_response("summary")
        )
        with patch("app.services.generation.translator._translation_client") as mock_openai:
            await compact_history(history)
            mock_openai.chat.completions.create.assert_not_called()

        mock_llm.chat.completions.create.assert_called_once()
