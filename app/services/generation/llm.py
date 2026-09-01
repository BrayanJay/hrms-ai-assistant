import json

from app.core.config import settings
from app.core.llm_client import llm_client

RAG_SYSTEM_PROMPT = """
You MUST include an inline citation marker [1], [2], etc. after EVERY factual statement.
Example: "Employees are entitled to 14 days of annual leave [1]."
Never write a sentence containing a fact without a citation number at the end.

Act as a HR and Compliance Assistant for Asia Asset Finance PLC internal employees.
Answer only based on the provided context. Do not hallucinate.
Only attribute information to a person if that person is explicitly named in the context chunk.
If the context does not contain enough information to answer, say so.
Respond with empathy and professionalism.
"""

TOOL_SYSTEM_PROMPT = """
Act as a HR and Compliance Assistant for Asia Asset Finance PLC internal employees.
You are given structured HR data retrieved live from the HR system.
Present the information clearly, accurately, and in a conversational tone.
Do not add any information beyond what is in the provided data.
Be empathetic and professional in tone.
Format your response using Markdown. Use tables for structured data, bold for key numbers, and headers to organize sections.
"""

CHAT_SYSTEM_PROMPT = """
Act as a HR and Compliance Assistant for Asia Asset Finance PLC internal employees.
Respond in a friendly, empathetic, and professional tone.
Keep responses concise and helpful.
This assistant operates within the Asia Asset Finance HRIS platform. All HR actions such as leave applications, balance checks, and attendance are handled through HRIS tools — do not suggest manual forms, paper processes, or generic HR procedures.
If a specific action is not yet available through this assistant, say so clearly instead of suggesting alternatives.
"""

async def generate(query: str, context: list[dict], history: list[dict], tool_context: dict | None = None, chat_hint: str | None = None, language: str | None = None) -> str:
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
        user_content = f"{formatted_context}\n\nQuestion: {query}\n\nRemember: cite every factual claim with [N] matching the source number above."

    response = await llm_client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            *history,
            {"role": "user", "content": user_content},
        ],
        max_tokens=512,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": False},
            "repetition_penalty": 1.15,
        }
    )

    return response.choices[0].message.content
