import json

from app.core.config import settings
from app.core.llm_client import llm_client

RAG_SYSTEM_PROMPT = """
Act as a HR and Compliance Assistant for Asia Asset Finance PLC internal employees.
Answer only based on the provided context. Do not hallucinate.
Only attribute information to a person if that person is explicitly named in the context chunk.
If a chunk does not mention a person by name, do not use it to describe that person.
Show inline citations for every claim [1], [2], [3].
If the context does not contain enough information to answer, say so.
"""

TOOL_SYSTEM_PROMPT = """
Act as a HR and Compliance Assistant for Asia Asset Finance PLC internal employees.
You are given structured HR data retrieved live from the HR system.
Present the information clearly, accurately, and in a conversational tone.
Do not add any information beyond what is in the provided data.
"""

CHAT_SYSTEM_PROMPT = """
Act as a HR and Compliance Assistant for Asia Asset Finance PLC internal employees.
Respond in a friendly, empathetic, and professional tone.
Keep responses concise and helpful.
"""

async def generate(query: str, context: list[dict], history: list[dict], tool_context: dict | None = None, chat_hint: str | None = None ) -> str:
    if chat_hint:
        system = CHAT_SYSTEM_PROMPT + f"\nHint: {chat_hint}"
        user_content = query

    elif tool_context and context:
        formatted_context = "\n".join(
            f"[{c['citation']}] (doc: {c['doc_id']}) {c['content']}"
            for c in context if c["type"] != "image"
        )
        system = RAG_SYSTEM_PROMPT
        user_content = (
            f"Policy context:\n{formatted_context}\n\n"
            f"HR system data:\n{json.dumps(tool_context, indent=2)}\n\n"
            f"Question: {query}"
        )

    elif tool_context:
        system = TOOL_SYSTEM_PROMPT
        user_content = (
            f"HR system data:\n{json.dumps(tool_context, indent=2)}\n\n"
            f"Question: {query}"
        )

    else:
        formatted_context = "\n".join(
            f"[{c['citation']}] (doc: {c['doc_id']}) {c['content']}"
            for c in context if c["type"] != "image"
        )
        system = RAG_SYSTEM_PROMPT
        user_content = f"{formatted_context}\n\nQuestion: {query}"

    response = await llm_client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            *history,
            {"role": "user", "content": user_content},
        ],
    )

    return response.choices[0].message.content
