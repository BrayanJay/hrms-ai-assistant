from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


SYSTEM_PROMPT = """
Act as a HR and Compliance Assistant for Asia Asset Finance PLC internal employees.
Answer only based with the provided context and do not hallucinate.
Show inline citations every claim [1], [2], [3].
If the context doesn't contain the answer, say you don't have enough information.
"""

async def generate(query: str, context: list[dict]) -> str:

    formatted_context = "\n".join([f"[{c['citation']}] {c["content"]}" for c in context if c["type"] != "image"])

    response = await client.chat.completions.create(messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{formatted_context}\n\nQuestion: {query}"}
    ],
    model=settings.openai_model
    )

    return response.choices[0].message.content