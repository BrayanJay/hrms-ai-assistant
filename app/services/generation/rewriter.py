from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


SYSTEM_PROMPT = """
Rewrite the query to be specific and retrieval friendly.
Preserve the original content and do not use out of the topic words.
Return only the rewritten query, nothing else
"""
async def rewrite(query: str) -> str:
    response = await client.chat.completions.create(messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ],
    model=settings.openai_model
    )

    return response.choices[0].message.content