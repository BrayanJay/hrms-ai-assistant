from app.core.llm_client import llm_client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_SUMMARY_PROMPT = (
    "You are summarizing a conversation between an employee and an HR assistant. "
    "Write a concise summary (3–6 sentences) covering: topics asked, information provided, "
    "and any decisions or actions taken. Write in third person, past tense."
)


def _char_count(messages: list[dict]) -> int:
    return sum(len(m.get("content", "")) for m in messages)


async def _summarize(messages: list[dict]) -> str:
    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages
    )
    response = await llm_client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": _SUMMARY_PROMPT},
            {"role": "user", "content": f"Summarize this conversation:\n\n{transcript}"},
        ],
        max_tokens=256,
        extra_body={"enable_thinking": False, "repetition_penalty": 1.15},
    )
    return response.choices[0].message.content


async def compact_history(history: list[dict]) -> list[dict]:
    if _char_count(history) <= settings.history_compact_threshold:
        return history

    if len(history) <= settings.history_keep_recent:
        return history

    old_turns = history[:-settings.history_keep_recent]
    recent_turns = history[-settings.history_keep_recent:]

    logger.info("compacting history", extra={"old_turns": len(old_turns), "recent_turns": len(recent_turns)})

    summary = await _summarize(old_turns)

    return [
        {"role": "user", "content": f"[Earlier conversation summary]\n{summary}"},
        {"role": "assistant", "content": "Understood, I have context from our earlier conversation."},
        *recent_turns,
    ]
