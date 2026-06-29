# Sprint 1 Task Plan
# Astrynox AI — Foundation & Auth

**Sprint Duration:** Wed 17 Jun → Tue 23 Jun 2026  
**Goal:** Docker services running, full authentication system (email/OTP + Google), admin document upload endpoint, and admin dashboard UI.  
**Daily commitment:** 5–7 hours

---

## Flows Overview

Sprint 1 is broken into 5 sequential flows. Each flow must be complete before the next one begins — auth depends on Docker, the frontend depends on the backend endpoints.

```
Flow 1 — Infrastructure & Docker          Wed 17 Jun
Flow 2 — Backend Auth (Email/OTP/JWT)     Thu 18 Jun
Flow 3 — Backend Auth (Google OAuth2)     Fri 19 Jun
Flow 4 — Admin Document Upload API        Sat 20 Jun
Flow 5a — Frontend Auth Pages             Mon 22 Jun
Flow 5b — Admin Dashboard UI              Tue 23 Jun
```

---

## Flow 1 — Infrastructure & Docker

**What this is:** Before any code runs, the services it depends on (PostgreSQL, Redis, Qdrant) must be containerized and reachable. FastAPI also needs its entry point, settings loader, and CORS wired up. This flow produces a running local environment with nothing built into it yet.

**Why this order:** Every flow after this connects to at least one of these services. Doing infra first means when something breaks later, you know it's not the infrastructure.

### Tasks

| # | Task | File | Done |
|---|------|------|------|
| 1.1 | Write Docker Compose — 4 services: `postgres`, `qdrant`, `redis`, `backend` with correct ports, volumes, env_file | `docker-compose.yml` | [ ] |
| 1.2 | Implement `config.py` — Pydantic `BaseSettings` loading all `.env` variables with correct types | `app/core/config.py` | [ ] |
| 1.3 | Implement `logging.py` — structured logging setup (timestamp, level, message) | `app/core/logging.py` | [ ] |
| 1.4 | Implement `main.py` — FastAPI app init, CORS middleware (whitelist frontend origin), register route prefixes | `app/main.py` | [ ] |
| 1.5 | Initialize Alembic | `alembic/` | [ ] |
| 1.6 | **Scratch:** `scratch/test_fastapi.py` — one GET route, run `uvicorn`, hit it in browser | `scratch/test_fastapi.py` | [ ] |
| 1.7 | **Verify:** `docker-compose up -d` → all 4 services show `running`. FastAPI Swagger at `localhost:8000/docs` | — | [ ] |

**Concepts to understand before coding:**
- What CORS is and why the frontend origin must be whitelisted (browsers block cross-origin requests by default)
- What `BaseSettings` does differently from a plain class — it reads from env vars and validates types at startup
- What a Docker volume is and why data disappears without one

---

## Flow 2 — Backend Auth (Email / Password / OTP / JWT)

**What this is:** The complete email-based authentication cycle — register a user, log in, receive an OTP by email, verify it, and receive a JWT. This covers the full security layer: password hashing, token creation, OTP generation and expiry, and the Resend email integration.

**Why this before Google OAuth2:** Google auth reuses the JWT issuance logic from this flow. Build it here once, then Google OAuth just plugs into the same `create_jwt()` call.

### Tasks

| # | Task | File | Done |
|---|------|------|------|
| 2.1 | Implement `security.py` — `hash_password()`, `verify_password()`, `create_access_token()`, `create_refresh_token()`, `decode_token()`, `generate_otp()` (6-digit), `hash_otp()` | `app/core/security.py` | [ ] |
| 2.2 | Implement `user.py` SQLAlchemy model — fields: `id (uuid)`, `email`, `password_hash`, `google_id`, `role (enum)`, `is_verified`, `created_at` | `app/models/user.py` | [ ] |
| 2.3 | Implement `otp.py` SQLAlchemy model — fields: `id`, `otp_token`, `otp_code (hashed)`, `user_id (FK)`, `is_used`, `expires_at`, `created_at` | `app/models/otp.py` | [ ] |
| 2.4 | Create Alembic migration for `users` and `otp` tables, run `alembic upgrade head` | `alembic/versions/` | [ ] |
| 2.5 | Implement `auth_service.py` — `register_user()`, `login_user()` (verify password → generate OTP → send via Resend → return otp_token), `verify_otp()` (validate code, expiry, used flag → issue JWT) | `app/services/auth_service.py` | [ ] |
| 2.6 | Implement `auth.py` routes — `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/verify-otp`, `POST /api/auth/refresh`, `POST /api/auth/logout` | `app/api/routes/auth.py` | [ ] |
| 2.7 | Implement auth Pydantic schemas — `RegisterRequest`, `LoginRequest`, `OTPVerifyRequest`, `TokenResponse`, `UserResponse` | `app/schemas/auth.py` | [ ] |
| 2.8 | **Scratch:** `scratch/test_jwt.py` — generate an access token, decode it, print payload, verify it rejects an expired token | `scratch/test_jwt.py` | [ ] |
| 2.9 | **Verify end-to-end:** `POST /register` → `POST /login` → OTP arrives in email → `POST /verify-otp` → JWT returned. Then test: wrong OTP rejected, expired OTP rejected, duplicate registration rejected | — | [ ] |

**Concepts to understand before coding:**
- Why passwords are hashed (bcrypt) and never stored plain — and what a cost factor of 12 means
- The difference between an access token (short-lived, 15 min) and a refresh token (long-lived, 7 days) and why both exist
- Why the OTP is stored hashed, not plain, even though it's temporary
- What `sub` in a JWT payload means and why it's a UUID, not the email

---

## Flow 3 — Backend Auth (Google OAuth2)

**What this is:** The Google login path. The user clicks "Login with Google", Google redirects back with an auth code, your backend exchanges that code for an `id_token`, verifies it, finds or creates the user, and issues your own JWT. No OTP involved.

**Why separate from Flow 2:** The OAuth2 dance is a distinct protocol from email/password. Keeping it separate in the plan makes it easier to reason about and debug independently.

### Tasks

| # | Task | File | Done |
|---|------|------|------|
| 3.1 | Create Google Cloud project, enable Google Identity API, create OAuth2 credentials (Web app), set redirect URI to `http://localhost:3000/auth/google/callback`, copy Client ID + Secret to `.env` | Google Cloud Console | [ ] |
| 3.2 | Add `exchange_google_code()` to `auth_service.py` — exchange auth code for tokens via Google token endpoint, verify `id_token`, extract `google_id` + `email` | `app/services/auth_service.py` | [ ] |
| 3.3 | Add `find_or_create_google_user()` to `auth_service.py` — look up user by `google_id`, create if not found (no password_hash, no OTP), issue JWT | `app/services/auth_service.py` | [ ] |
| 3.4 | Add `POST /api/auth/google` route — accepts `{code}`, calls service, returns JWT | `app/api/routes/auth.py` | [ ] |
| 3.5 | **Scratch:** `scratch/test_google_oauth.py` — manually paste a valid auth code, run the exchange, print the decoded user info | `scratch/test_google_oauth.py` | [ ] |
| 3.6 | **Verify end-to-end:** Google login flow in Swagger or Postman — valid code → JWT returned. Test invalid/expired code → 401 returned | — | [ ] |

**Concepts to understand before coding:**
- The OAuth2 authorization code flow — why the frontend gets the code but the backend exchanges it (the secret never touches the browser)
- What `id_token` is vs `access_token` in Google's response — you verify the `id_token`, not the `access_token`
- Why you verify the `id_token` server-side with Google's public keys rather than trusting it blindly

---

## Flow 4 — Admin Document Upload API

**What this is:** The admin-only endpoint that accepts a file upload, validates it, creates a database record with status "processing", and returns a document ID. This does not trigger the ingestion pipeline yet — that is Sprint 2. This flow also wires up the JWT dependency system so routes can require authentication and role checks.

**Why status stays "processing" for now:** The actual ingestion pipeline (parsing, chunking, embedding) is Sprint 2. The upload endpoint's job is intake and recording only.

### Tasks

| # | Task | File | Done |
|---|------|------|------|
| 4.1 | Implement `dependencies.py` — `get_current_user()` (decode JWT from Authorization header), `require_admin()` (check `role == "admin"`, raise 403 otherwise) | `app/api/dependencies.py` | [ ] |
| 4.2 | Implement `document.py` SQLAlchemy model — fields: `id (uuid)`, `filename`, `original_filename`, `file_type (enum)`, `source_type (enum)`, `status (enum: processing/completed/failed)`, `total_chunks`, `completed_chunks`, `error_message`, `uploaded_by (FK → users)`, `created_at`, `completed_at` | `app/models/document.py` | [ ] |
| 4.3 | Create Alembic migration for `documents` table, run `alembic upgrade head` | `alembic/versions/` | [ ] |
| 4.4 | Implement document Pydantic schemas — `DocumentUploadResponse`, `DocumentListResponse`, `DocumentRow` | `app/schemas/document.py` | [ ] |
| 4.5 | Implement `POST /api/documents/upload` — validate MIME type + extension (allowed: pdf, docx, pptx, html, xlsx, csv), extract metadata (filename, size), create DB record with `status: processing`, return `document_id` + `status` | `app/api/routes/documents.py` | [ ] |
| 4.6 | Implement `GET /api/documents/` — list all documents with status (admin only) | `app/api/routes/documents.py` | [ ] |
| 4.7 | Implement `DELETE /api/documents/{id}` — delete DB record (Qdrant removal comes in Sprint 2) | `app/api/routes/documents.py` | [ ] |
| 4.8 | **Scratch:** `scratch/test_upload.py` — minimal FastAPI endpoint that accepts a file and prints filename + MIME type | `scratch/test_upload.py` | [ ] |
| 4.9 | **Verify:** Upload PDF as admin → record in PostgreSQL with status "processing". Upload with non-admin JWT → 403. Upload `.exe` → 400. Upload without JWT → 401 | — | [ ] |

**Concepts to understand before coding:**
- How FastAPI `Depends()` works — it's a dependency injection system, not middleware. `require_admin` wraps `get_current_user` and adds the role check on top
- Why MIME type alone is not enough for file validation — browsers can lie about content type, so you also check the extension
- Why the document status is "processing" from the moment of upload, not after ingestion completes

---

## Flow 5a — Frontend Auth Pages

**What this is:** The login, register, and OTP verification pages in Next.js. The Axios API client that attaches JWTs to every request. The token storage and refresh logic. By end of this flow, a user can complete the full auth flow in the browser.

**Why frontend after all backend:** You cannot test the frontend auth pages without working backend endpoints. The backend must be done first.

### Tasks

| # | Task | File | Done |
|---|------|------|------|
| 5a.1 | Implement `api.ts` — Axios instance with `baseURL`, request interceptor (attach `Authorization: Bearer <token>`), response interceptor (catch 401 → trigger refresh) | `frontend/lib/api.ts` | [ ] |
| 5a.2 | Implement `auth.ts` — `getAccessToken()`, `setTokens()`, `clearTokens()`, `refreshAccessToken()` using localStorage | `frontend/lib/auth.ts` | [ ] |
| 5a.3 | Implement `types.ts` — TypeScript types: `User`, `TokenResponse`, `Document`, `Citation`, `QueryResponse` matching the API schemas | `frontend/lib/types.ts` | [ ] |
| 5a.4 | Implement register page — email + password form, calls `POST /api/auth/register`, redirects to login on success | `frontend/app/auth/register/page.tsx` | [ ] |
| 5a.5 | Implement login page — email + password form, calls `POST /api/auth/login`, stores `otp_token`, redirects to `/auth/verify-otp`. Google login button triggers OAuth2 redirect | `frontend/app/auth/login/page.tsx` | [ ] |
| 5a.6 | Implement OTP verify page — 6-digit input, calls `POST /api/auth/verify-otp` with stored `otp_token`, stores JWT, redirects to `/chat` | `frontend/app/auth/verify-otp/page.tsx` | [ ] |
| 5a.7 | Implement Google OAuth2 callback handling — extract code from URL, POST to `/api/auth/google`, store JWT, redirect to `/chat` | `frontend/app/auth/google/callback/` | [ ] |
| 5a.8 | **Verify:** Full login flow in browser — email login → OTP email → verify → redirect to `/chat`. Google login → redirect to `/chat`. Invalid credentials → error shown. Invalid OTP → error shown | — | [ ] |

**Concepts to understand before coding:**
- Why tokens are stored in `localStorage` for this MVP (simple, works) and what the tradeoff is (XSS risk — HttpOnly cookies are safer but more complex to implement)
- What the Axios interceptor pattern does — it's a middleware for HTTP calls, not per-component logic
- Why the OTP page needs the `otp_token` (it's the session binding between login step and verify step — prevents anyone from verifying an OTP without having gone through login)

---

## Flow 5b — Admin Dashboard UI

**What this is:** The admin-only page that lists uploaded documents, shows their ingestion status, and provides the upload form. Uses TanStack Query for data fetching and mutations so the list updates automatically after an upload or delete.

### Tasks

| # | Task | File | Done |
|---|------|------|------|
| 5b.1 | Implement `useDocuments.ts` hook — `useQuery` for document list (`GET /api/documents/`), `useMutation` for upload (`POST /api/documents/upload`), `useMutation` for delete (`DELETE /api/documents/{id}`) | `frontend/hooks/useDocuments.ts` | [ ] |
| 5b.2 | Implement `StatusBadge.tsx` — renders color-coded badge: processing (yellow), completed (green), failed (red) | `frontend/components/admin/StatusBadge.tsx` | [ ] |
| 5b.3 | Implement `DocumentRow.tsx` — filename, file type, status badge, upload date, delete button | `frontend/components/admin/DocumentRow.tsx` | [ ] |
| 5b.4 | Implement `DocumentList.tsx` — renders list of `DocumentRow`, empty state when no documents | `frontend/components/admin/DocumentList.tsx` | [ ] |
| 5b.5 | Implement `UploadForm.tsx` — file input (accept only allowed types), upload button, shows loading state while uploading, error if rejected | `frontend/components/admin/UploadForm.tsx` | [ ] |
| 5b.6 | Implement admin documents page — assembles `DocumentList` + `UploadForm`, protected (redirect non-admin to `/chat`) | `frontend/app/admin/documents/page.tsx` | [ ] |
| 5b.7 | Configure TanStack Query client | `frontend/lib/query-client.ts` | [ ] |
| 5b.8 | **Verify:** Upload a file → appears in list with "processing" status. Delete a document → removed from list. Non-admin user visits `/admin` → redirected. Status badge colors correct | — | [ ] |

**Concepts to understand before coding:**
- What `useQuery` vs `useMutation` is — `useQuery` is for reads (runs automatically, caches), `useMutation` is for writes (triggered manually, has loading/error state)
- Why `invalidateQueries` is called after a mutation — it tells TanStack to refetch the document list so the UI reflects the change
- Why the admin check belongs in the page component (and potentially middleware), not just the API — defense in depth

---

## Daily Schedule

| Date | Day | Flow | Focus |
|------|-----|------|-------|
| Wed 17 Jun | Day 1 | Flow 1 | Docker Compose, `config.py`, `logging.py`, `main.py`, Alembic init |
| Thu 18 Jun | Day 2 | Flow 2 | `security.py`, User + OTP models, migration, `auth_service.py`, auth routes |
| Fri 19 Jun | Day 3 | Flow 3 | Google Cloud setup, `exchange_google_code()`, `/api/auth/google` route |
| Sat 20 Jun | Day 4 | Flow 4 | `dependencies.py`, Document model, migration, upload + list + delete endpoints |
| Mon 22 Jun | Day 5 | Flow 5a | `api.ts`, `auth.ts`, login/register/OTP pages, Google callback |
| Tue 23 Jun | Day 6 | Flow 5b | TanStack hooks, admin UI components, documents page, sprint review |

---

## Sprint 1 — Definition of Done

Check every item before calling this sprint complete:

- [ ] `docker-compose up -d` → all services healthy
- [ ] FastAPI Swagger accessible at `localhost:8000/docs`
- [ ] Register → email login → OTP in email → verify → JWT issued
- [ ] Google OAuth2 login → JWT issued (no OTP)
- [ ] Wrong OTP → 401. Expired OTP → 401. Duplicate registration → 400
- [ ] Admin uploads a PDF → DB record created with status "processing"
- [ ] Non-PDF upload → 400 with clear error message
- [ ] Non-admin JWT on admin endpoint → 403
- [ ] No JWT on protected endpoint → 401
- [ ] Admin dashboard lists uploaded documents with correct status badges
- [ ] Delete a document → removed from list
- [ ] Google OAuth2 login button in frontend works end-to-end

---

## Carry-Forward (Intentionally Deferred to Sprint 2)

These are out of scope for this sprint — do not start them:

- Ingestion pipeline (parse, chunk, embed, store) — Sprint 2
- Document status update from "processing" to "completed/failed" — Sprint 2
- Qdrant deletion on document delete — Sprint 2
- Web scraping endpoint — Sprint 2
- Chat page and query endpoint — Sprint 3/4

---

*Sprint 1 | Astrynox AI | Start: 2026-06-17 | End: 2026-06-23*
