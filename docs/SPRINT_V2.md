# Sprint Plan
# Astrynox AI — V2 Agentic Router + Tool Calling

**Version:** 1.0  
**Sprint:** V2 Development  
**Duration:** 8 Days — 1 Aug 2026 to 8 Aug 2026  
**Developer:** Brayan K. Jayawardhana  
**Reference:** `docs/SDD_V2.md`

---

## Sprint Goal

Build and integrate the V2 agentic layer on top of the existing V1 RAG system:
- LLM-based intent router (RAG / TOOL / BOTH / CHAT)
- HR System API tool calling (read-only, phase 1)
- Maker-checker confirmation flow for write operations
- Trilingual + empathetic response generation
- Full audit logging via AgentLog
- Frontend confirmation UI

---

## Daily Plan

### Day 1 — Friday 1 Aug | Foundation

**Goal:** Database model, config wiring, environment setup.

| # | Task | File | Type |
|---|---|---|---|
| 1 | Add `AgentLog` SQLAlchemy model | `app/models/agent_log.py` | New file |
| 2 | Register model in Alembic | `alembic/env.py` | Update |
| 3 | Run Alembic migration | — | Terminal |
| 4 | Add new env vars to `config.py` | `app/core/config.py` | Update |
| 5 | Update `.env` and `.env.sample` | `.env`, `.env.sample` | Update |
| 6 | Add `httpx` to `requirements.txt` | `requirements.txt` | Update |

**New env vars to add:**
```env
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o
HR_API_BASE_URL=https://hr.internal.company.com/api/v1
HR_API_TOKEN=shared_service_token_here
```

**AgentLog fields:** `id`, `user_id`, `session_id`, `query`, `intent`, `router_decision` (JSON), `tool_name`, `tool_params` (JSON), `tool_response` (JSON), `maker_checker_status`, `created_at`

**Done when:** migration runs clean, `agent_logs` table exists in PostgreSQL.

---

### Day 2 — Saturday 2 Aug | Schemas + Tool Registry

**Goal:** All Pydantic schemas defined. Tool definitions written.

| # | Task | File | Type |
|---|---|---|---|
| 1 | Create `RouterDecision` schema | `app/schemas/agent.py` | New file |
| 2 | Create `ConfirmRequest` schema | `app/schemas/agent.py` | Same file |
| 3 | Add confirmation fields to `QueryResponse` | `app/schemas/query.py` | Update |
| 4 | Write phase 1 tool definitions | `app/services/tools/registry.py` | New file |

**`RouterDecision` fields:** `intent`, `language`, `rag_query`, `tool_name`, `tool_params`, `is_sequential`, `is_write`, `chat_response_hint`

**`QueryResponse` additions:** `requires_confirmation: bool`, `confirmation_payload: dict | None`, `pending_action_id: str | None`

**Phase 1 tools to define in registry:**
- `get_leave_balance` — remaining leave by type
- `get_kpi_achievement` — KPI score and status
- `get_team_members` — team members under same manager
- `get_directory_details` — contact details by role or name
- `get_payslip_summary` — salary and deduction summary

Each tool definition must include: `name`, `description`, `parameters` (JSON Schema), `endpoint`, `method`, `is_write: false`

**Done when:** schemas import without errors, all 5 tools defined in registry.

---

### Day 3 — Sunday 3 Aug | Tool Executor + Pending Store

**Goal:** HTTP client for HR API calls. Redis store for maker-checker.

| # | Task | File | Type |
|---|---|---|---|
| 1 | Build tool executor HTTP client | `app/services/tools/executor.py` | New file |
| 2 | Add mock response fallback for missing HR API | `app/services/tools/executor.py` | Same file |
| 3 | Build Redis pending action store | `app/services/tools/pending.py` | New file |

**Executor responsibilities:**
- Look up tool from registry
- Build URL from endpoint pattern + params
- Add `Authorization: Bearer {HR_API_TOKEN}` header
- Call HR API via `httpx.AsyncClient`
- Return JSON response or raise `ToolCallError`
- Mock mode: if `HR_API_BASE_URL` is not set, return realistic mock data per tool

**Pending store responsibilities:**
- `set_pending(session_id, action_id, payload)` → Redis key with 300s TTL
- `get_pending(session_id, action_id)` → return payload or None
- `delete_pending(session_id, action_id)` → remove after confirmation

**Done when:** executor returns mock data for all 5 tools, pending store sets/gets/deletes correctly.

---

### Day 4 — Monday 4 Aug | LLM Client + Intent Router

**Goal:** Abstracted LLM client. Router classifies all 4 intents correctly.

| # | Task | File | Type |
|---|---|---|---|
| 1 | Create shared LLM client | `app/core/llm_client.py` | New file |
| 2 | Build intent router | `app/services/router/intent.py` | New file |
| 3 | Write router system prompt | `app/services/router/intent.py` | Same file |
| 4 | Test router manually with sample queries | — | Terminal / Swagger |

**LLM client:** single `AsyncOpenAI` instance using `settings.llm_base_url`, `settings.llm_api_key`. Model passed per call via `settings.llm_model`. Imported by both router and generator.

**Router function signature:**
```python
async def classify_intent(query: str, user_id: str, history: list[dict]) -> RouterDecision
```

**Test cases to verify (all 4 intents):**

| Query | Expected Intent |
|---|---|
| "What is the company maternity leave policy?" | RAG |
| "What is my leave balance?" | TOOL → get_leave_balance |
| "Am I eligible for the bonus given my KPI?" | BOTH (sequential) |
| "I don't feel well today" | CHAT |
| " මගේ නිවාඩු ශේෂය කීයද?" | TOOL → language: si |
| "en leave balance evvalavu?" | TOOL → language: ta |

**Done when:** router returns correct `RouterDecision` for all 6 test queries above.

---

### Day 5 — Tuesday 5 Aug | Orchestrator Rewrite

**Goal:** `query.py` orchestrates all 4 intent paths. `/confirm` endpoint live.

| # | Task | File | Type |
|---|---|---|---|
| 1 | Rewrite `query.py` orchestrator | `app/api/routes/query.py` | Major rewrite |
| 2 | Add `POST /api/query/confirm` endpoint | `app/api/routes/query.py` | Same file |
| 3 | Wire AgentLog write after every query | `app/api/routes/query.py` | Same file |

**Orchestrator flow:**
```
1. Call classify_intent() → RouterDecision
2. Dispatch based on intent:
   RAG  → existing retrieve() + generate()
   TOOL → check is_write:
            True  → build confirmation payload, store in Redis, return requires_confirmation: true
            False → execute_tool() → generate()
   BOTH → parallel or sequential based on is_sequential flag
   CHAT → generate() with empathy context, no RAG, no tool
3. Write AgentLog row
4. Return QueryResponse
```

**Caching rule:** only call `set_answer()` on pure RAG responses. Never cache TOOL, BOTH, or CHAT responses.

**Done when:** all 4 intent paths return correct responses via Swagger. AgentLog row written for each.

---

### Day 6 — Wednesday 6 Aug | Generation Update + Integration Testing

**Goal:** Generator updated for trilingual + empathetic output. Full pipeline tested end-to-end.

| # | Task | File | Type |
|---|---|---|---|
| 1 | Update `generate()` system prompt | `app/services/generation/llm.py` | Update |
| 2 | Update LLM client call to use shared client | `app/services/generation/llm.py` | Update |
| 3 | Test RAG path end-to-end | — | Manual |
| 4 | Test TOOL path end-to-end (mock data) | — | Manual |
| 5 | Test BOTH path — parallel | — | Manual |
| 6 | Test CHAT path — empathetic response | — | Manual |
| 7 | Test Sinhala and Tamil queries | — | Manual |

**Updated system prompt must:**
- Always respond in `{language}` (en / si / ta)
- Be empathetic first on sensitive queries
- Offer a relevant follow-up action when `chat_response_hint` is set
- Never expose tool names, API responses, or internal system details
- Maintain V1 citation format for RAG-sourced answers

**Done when:** all 4 paths tested and correct. Trilingual responses verified.

---

### Day 7 — Thursday 7 Aug | Frontend Confirmation UI

**Goal:** Chat page renders Confirm/Cancel buttons for maker-checker. Full write flow tested.

| # | Task | File | Type |
|---|---|---|---|
| 1 | Update `QueryResponse` TypeScript type | `frontend/lib/types.ts` or inline | Update |
| 2 | Add confirmation UI to chat page | `frontend/app/chat/page.tsx` | Update |
| 3 | Wire Confirm button → `POST /api/query/confirm` | `frontend/app/chat/page.tsx` | Update |
| 4 | Wire Cancel button → `POST /api/query/confirm` with `confirmed: false` | `frontend/app/chat/page.tsx` | Update |
| 5 | Test maker-checker flow end-to-end | — | Browser |

**Confirmation UI behaviour:**
- When `requires_confirmation: true` → render a structured card with action details + Confirm + Cancel buttons
- Buttons replace the chat input during confirmation — user cannot send a new query until they respond
- On Confirm: call `/api/query/confirm` → display result in chat
- On Cancel: call `/api/query/confirm` with `confirmed: false` → display cancellation message
- After either action: restore normal chat input

**Done when:** full maker-checker flow works in browser — apply leave → confirmation card → confirm → success message.

---

### Day 8 — Friday 8 Aug | Polish, Audit Verification + PR

**Goal:** Clean up, verify audit trail, commit, raise PR.

| # | Task |
|---|---|
| 1 | Verify `agent_logs` table has correct rows for all intent types |
| 2 | Verify `maker_checker_status` is set correctly (pending → confirmed / cancelled) |
| 3 | Verify tool results are never in Redis cache |
| 4 | Check all error paths return clean user-facing messages |
| 5 | Remove any debug logs or leftover mock print statements |
| 6 | Commit all changes with descriptive message |
| 7 | Raise PR: dev → main |

---

## File Checklist

| File | Status |
|---|---|
| `app/models/agent_log.py` | New |
| `app/schemas/agent.py` | New |
| `app/core/llm_client.py` | New |
| `app/services/router/intent.py` | New |
| `app/services/tools/registry.py` | New |
| `app/services/tools/executor.py` | New |
| `app/services/tools/pending.py` | New |
| `app/schemas/query.py` | Updated |
| `app/api/routes/query.py` | Major rewrite |
| `app/services/generation/llm.py` | Updated |
| `app/core/config.py` | Updated |
| `alembic/env.py` | Updated |
| `.env` / `.env.sample` | Updated |
| `requirements.txt` | Updated |
| `frontend/app/chat/page.tsx` | Updated |

---

## Risk Log

| Risk | Likelihood | Mitigation |
|---|---|---|
| HR API docs not available | High | Mock executor returns realistic data — executor is the only file that changes when real docs arrive |
| Router JSON conformance issues | Medium | Build JSON parse retry in router, validate against Pydantic schema, fallback to RAG if parse fails |
| Qwen 3 tool calling reliability (prod) | Medium | Test thoroughly with `--tool-call-parser hermes`; router prompt includes explicit JSON schema |
| BOTH sequential path edge cases | Low | Test with at least 2 sequential queries before Day 6 |
| Redis TTL expiry during maker-checker | Low | Return "confirmation expired, please try again" — user re-sends the original query |

---

*Astrynox AI — Sprint V2 Plan | 1–8 Aug 2026*
