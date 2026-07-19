from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


SYSTEM_PROMPT = """
Act as a HR and Compliance Assistant for Asia Asset Finance PLC internal employees.
Answer only based on the provided context. Do not hallucinate.
Only attribute information to a person if that person is explicitly named in the context chunk.
If a chunk does not mention a person by name, do not use it to describe that person.
Show inline citations for every claim [1], [2], [3].
If the context does not contain enough information to answer, say so.
"""

async def generate(query: str, context: list[dict], history: list[dict]) -> str:

    formatted_context = "\n".join([f"[{c['citation']}] (doc: {c['doc_id']}) {c['content']}" for c in context if c["type"] != "image"])

    response = await client.chat.completions.create(messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": f"{formatted_context}\n\nQuestion: {query}"}
    ],
    model=settings.openai_model
    )

    return response.choices[0].message.content