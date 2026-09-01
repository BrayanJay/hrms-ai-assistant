import json
from app.core.llm_client import llm_client
from app.core.config import settings
from app.schemas.agent import RouterDecision

from app.services.tools.registry import TOOL_REGISTRY

tool_descriptions = "\n".join(
    f"- {tool['name']}: {tool['description']}"
    for tool in TOOL_REGISTRY.values()
)

ROUTER_SYSTEM_PROMPT = f"""
  You are a query classifier for Asia Asset Finance HRIS AI Chatbot, an enterprise HR knowledge assistant.                                                                           
  Your only job is to analyze the user's query and return a JSON classification decision.

  ## INTENTS

  Choose exactly one:

  - RAG: The query asks about company policies, procedures, guidelines, or general HR knowledge
    that can be answered from the internal knowledge base.
    Examples: "What is the maternity leave policy?", "How do I apply for a promotion?"

  - TOOL: The query asks for personal, real-time HR data specific to the user
    (leave balances, KPI scores, payslips, team members, directory lookups).
    Examples: "What is my leave balance?", "Show me my payslip for July."

  - BOTH: The query requires BOTH knowledge base context AND personal HR data to answer fully.
    Examples: "Am I eligible for a bonus given my KPI score?"
    Set is_sequential: true only if the tool result is needed to form the RAG query.

  - CHAT: The query is conversational, emotional, or unrelated to HR data or policies.
    Examples: "I don't feel well today", "Thank you", "Good morning"

  ## AVAILABLE TOOLS

  Use these tool names exactly as written:

  {tool_descriptions}

  ## LANGUAGE DETECTION

  Detect the language of the query:
  - en: English
  - si: Sinhala
  - ta: Tamil

  ## CRITICAL RULE

  Classify the CURRENT user message ONLY based on what it is asking for.
  Do NOT let the conversation history influence your intent choice.
  A TOOL query must always be classified as TOOL even if all previous messages were CHAT.
  A RAG query must always be classified as RAG even after casual conversation.
  The history is provided only to resolve pronouns or references — not to guess intent from tone.

  ## OUTPUT FORMAT

  Return ONLY a valid JSON object. No explanation. No markdown. No code fences.

  {{
    "intent": "RAG" | "TOOL" | "BOTH" | "CHAT",
    "language": "en" | "si" | "ta",
    "rag_query": "<rewritten search query for the knowledge base, or null>",
    "tool_name": "<exact tool name from the list above, or null>",
    "tool_params": {{"<param>": "<value>"}} | null,
    "is_sequential": true | false,
    "is_write": false,
    "chat_response_hint": "<empathy or tone hint for the response generator, or null>"
  }}

  Rules:
  - rag_query must be set for RAG and BOTH intents, null for TOOL and CHAT
  - tool_name and tool_params must be set for TOOL and BOTH intents, null for RAG and CHAT
  - is_write is always false in phase 1 (read-only tools)
  - chat_response_hint should be set for CHAT intents involving sensitive or emotional topics
  - employee_id in tool_params should always be set to the string "CURRENT_USER"
    (the orchestrator will replace this with the real employee ID at runtime)
  """

async def classify_intent(query: str, user_id: str, history: list[dict]) -> RouterDecision:

    messages = [{"role": "system", "content": ROUTER_SYSTEM_PROMPT}]
    messages.append({"role": "user", "content": query})

    response = await llm_client.chat.completions.create(
      model=settings.llm_model,
      messages=messages,
      response_format={"type": "json_object"},
      extra_body={"chat_template_kwargs": {"enable_thinking": False}},
  )

    try:
        data = json.loads(response.choices[0].message.content)
        return RouterDecision(**data)
    except Exception:
        return RouterDecision(
            intent="RAG",
            language="en",
            rag_query=query,
            tool_name=None,
            tool_params=None,
            is_sequential=False,
            is_write=False,
            chat_response_hint=None,
        )