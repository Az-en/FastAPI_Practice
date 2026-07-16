# FastAPI Backend Roadmap: From Learning Project to Production-Grade

**Context:** A course/user management API (SQLite + SQLAlchemy + Alembic + JWT auth) with a repository/service layered architecture already in place. The goal below isn't "add more features" — it's to take this codebase through the same maturity curve a real backend goes through at a company, in an order that makes sense and that you can defend in an interview.

---

## Current State: What's Already Right

- Layered architecture (routes → services → repositories → models) is a real pattern, not boilerplate — most learning projects don't have this.
- Alembic migrations are set up and match the models.
- Password hashing via `pwdlib`/bcrypt, JWT-based auth, role-based route guards (`get_teacher_user`).
- Pydantic schemas separated from ORM models.

## Current State: What's Actively Wrong (fix before building on top)

| Issue | Where | Why it matters |
|---|---|---|
| Hardcoded JWT secret committed to source | `src/core/security.py` | Anyone with repo access can forge tokens for any user. This is the #1 thing a reviewer will flag. |
| Conflicting dependencies `jwt` **and** `pyjwt` | `pyproject.toml` | These are two unrelated PyPI packages that both provide an `import jwt` — a classic dependency-confusion footgun. |
| `CourseToUser` model is a broken stub | `src/models/course_to_user.py` | Typo'd `__table__name` (not `__tablename__`), no columns. It signals unfinished intent (enrollments) that nothing currently uses. |
| List endpoints return `404` on empty results | `userRoutes.py`, `courseRoutes.py` | An empty list is a valid, successful response (`200` + `[]`), not a "not found" error. This is a common anti-pattern reviewers notice immediately. |
| Debug/scratch code committed | `src/repositories/user_repo.py` (`if __name__ == "__main__"` block, commented-out queries) | Signals the repo hasn't been cleaned before sharing — small thing, easy fix, disproportionate impact on first impressions. |
| SQLite DB file (`app.db`) committed to git | repo root | Should never be versioned; `.gitignore` doesn't cover it. |
| No tests anywhere | whole repo | The single biggest gap for "production-ready." Everything else is secondary to this. |
| No config/settings layer | scattered constants (`DATABASE_URL`, `SECRET`) | Nothing distinguishes dev/test/prod; secrets and infra config are baked into source. |

Everything below assumes these get cleaned up first — they're small, and doing them signals discipline before anyone even reads your features.

---

## Phase 0 — Hygiene & Critical Fixes
**Effort: Small | Prerequisite for everything else**

1. **Move secrets out of source** — replace the hardcoded `SECRET` with an environment variable, generate it with `secrets.token_hex(32)`, and never commit it. Do this as part of Phase 1's settings module so it's not a throwaway fix.
2. **Resolve the `jwt`/`pyjwt` conflict** — drop the `jwt` package, keep `pyjwt` only, and verify `import jwt` resolves to the right library.
3. **Delete or gitignore `app.db`**, remove the debug `__main__` block and commented-out code in `user_repo.py`.
4. **Decide on `CourseToUser` now, act later** — leave a `# TODO(Phase 4): enrollment model` comment or delete the stub file entirely so it doesn't mislead readers. You'll build the real version in Phase 4.
5. **Add a linter/formatter** (`ruff` + `ruff format`, or `black`) and fix the tabs-vs-spaces inconsistency between `main.py` and the rest of the codebase. Add a `pre-commit` config. This is a 20-minute task that makes every subsequent diff look intentional.

*Why it matters:* None of this is impressive on its own, but leaving it in place undermines everything else you build. A reviewer who finds a hardcoded secret stops trusting the rest of the code.

---

## Phase 1 — Configuration Management
**Effort: Small–Medium | Depends on: Phase 0**

- Introduce `pydantic-settings` (`BaseSettings`) with a single `Settings` object: `DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRE_MINUTES`, `ENVIRONMENT` (`dev`/`test`/`prod`), `LOG_LEVEL`.
- Load from `.env` locally; `.env.example` committed, `.env` gitignored.
- Inject `Settings` via a FastAPI dependency (`get_settings`) rather than importing module-level constants — this is what makes later phases (testing with overrides, per-environment DB URLs) actually work.

*Why it matters:* This is the dependency that unlocks test isolation (Phase 2 needs a separate test DB URL), environment-specific behavior (Phase 5's Postgres-in-prod / SQLite-in-dev split), and is one of the first things a senior engineer looks for — "can I run this locally without editing source files?"

---

## Phase 2 — Testing Foundation
**Effort: Large | Depends on: Phase 1 (for test-specific settings/DB override)**

This is the highest-leverage phase in the whole roadmap. A layered architecture with zero tests reads as "structured but unverified." A layered architecture with good tests reads as "professional."

1. Add `pytest`, `pytest-cov`, `httpx` (for `TestClient`/`ASGITransport`) as dev dependencies.
2. Build a test fixture that spins up an isolated SQLite (or in-memory) database per test session, overriding `get_db` via FastAPI's `dependency_overrides`.
3. **Unit tests** for `CourseService` and repositories — e.g., `_ensure_instructor` rejecting a non-teacher, `update_course` partial updates.
4. **Integration tests** against the actual API surface: registration → login → authenticated course CRUD → 401/403 paths → duplicate `course_code` conflict.
5. Add a coverage gate (even a soft one, e.g. "core service logic at 80%+") and wire `pytest` into a `make test` / `uv run pytest` command documented in the README.

*Why it matters:* Tests are the thing that lets you refactor fearlessly in every later phase (async migration, error-handling overhaul, auth hardening) without breaking things silently. It's also the single most commonly checked box in a backend code review — reviewers will look for a `tests/` directory before anything else.

---

## Phase 3 — Error Handling & API Contract Consistency
**Effort: Medium | Depends on: Phase 2 (tests should exist before this refactor)**

- Replace the empty-list-returns-`404` pattern with correct `200 + []` responses.
- Add a proper exception hierarchy (`DomainError`, `NotFoundError`, `ConflictError`, `PermissionDeniedError`) raised from services/repositories, translated to HTTP responses by global exception handlers in `main.py` — instead of scattering `HTTPException` calls inside repositories and services (a repository shouldn't know about HTTP status codes at all; that's a layering violation worth fixing).
- Add a handler for `IntegrityError` (e.g. duplicate `course_code`, duplicate `email`) that returns a clean `409 Conflict` instead of an unhandled `500`.
- Add a catch-all `Exception` handler that returns a consistent error envelope (`{"detail": ..., "error_code": ...}`) and logs the stack trace server-side without leaking it to the client.
- Fix validation: use Pydantic's `EmailStr` for `email` fields instead of plain `str`, and let role validation happen at the schema layer (`UserRole` enum) instead of relying on catching `LookupError`/`StatementError` from SQLAlchemy as a validation mechanism.

*Why it matters:* This is where you demonstrate you understand FastAPI's error-handling model beyond `raise HTTPException` sprinkled everywhere — a clean separation between domain errors and HTTP semantics is a hallmark of code that's survived a real production incident.

---

## Phase 4 — Domain Model & Database Maturity
**Effort: Medium–Large | Depends on: Phase 2 (tests), Phase 1 (settings)**

1. **Implement the enrollment relationship properly** — a real `CourseToUser` (or rename to `Enrollment`) association table with a composite key or its own `id`, `enrolled_at` timestamp, and proper `relationship()` declarations on `User` and `Course` (`course.instructor`, `course.students`, `user.enrolled_courses`). This finally uses the many-to-many intent that was stubbed out.
2. **Add `created_at`/`updated_at`** to all models via a shared `TimestampMixin`.
3. **Migrate to async SQLAlchemy** — async engine, `AsyncSession`, `async def` route handlers and repository methods. This is a meaningful, resume-relevant upgrade: your routes are currently `def` (sync), which works but doesn't showcase why FastAPI is async-first. Do this *after* tests exist so you can verify behavior is unchanged.
4. **Add Postgres as the real target database**, with SQLite optionally retained just for fast local testing. Document connection pooling settings (`pool_size`, `max_overflow`) explicitly rather than relying on defaults.
5. Generate the Alembic migration for the enrollment table and timestamp columns.

*Why it matters:* This phase is where "I can use an ORM" becomes "I understand relational modeling and async I/O trade-offs." The instructor/enrollment relationship is also the first place you can showcase eager-loading (`selectinload`) to avoid N+1 queries — a very common interview topic.

---

## Phase 5 — Authentication & Security Hardening
**Effort: Medium–Large | Depends on: Phase 1 (settings for secrets)**

- Add **refresh tokens** alongside short-lived access tokens, with a `/users/refresh` endpoint and a proper logout/revocation strategy (e.g., a denylist table or short-lived access tokens + refresh rotation).
- Generalize the single `get_teacher_user` role check into a reusable **permission/scope system** (e.g., `require_role("teacher")` factory, or JWT scopes) so adding a third role later doesn't mean copy-pasting the same function.
- Add **rate limiting** on `/users/login` (e.g., `slowapi`) to blunt credential-stuffing/brute-force attempts.
- Add **CORS configuration** (explicit allowed origins from settings, not `*`) and basic security headers middleware (`X-Content-Type-Options`, `Strict-Transport-Security` if behind TLS).
- Enforce a minimum password policy at the schema layer.

*Why it matters:* Auth is where interviewers probe hardest, because it's where "it works" and "it's safe" diverge the most. Showing refresh-token rotation and rate limiting demonstrates you've thought about abuse, not just the happy path.

---

## Phase 6 — Observability
**Effort: Medium | Depends on: Phase 1 (settings for log level)**

- Structured logging (JSON via `structlog` or a configured `logging` formatter), replacing the single ad hoc `logger.info` call.
- **Request ID / correlation ID middleware** — generate or propagate an `X-Request-ID`, attach it to every log line for a request, return it in the response headers.
- `/health` (liveness) and `/ready` (readiness — checks DB connectivity) endpoints.
- Basic metrics via `prometheus-fastapi-instrumentator` (request count, latency histograms by route) — even without a running Prometheus/Grafana stack, exposing `/metrics` shows you understand the observability contract.

*Why it matters:* This is the phase that separates "a working API" from "an API someone could operate at 3am during an incident." Correlation IDs and structured logs are close to universal in real backend teams.

---

## Phase 7 — API Polish, Versioning & Pagination
**Effort: Medium | Depends on: Phase 3 (error handling), Phase 4 (relationships)**

- Add API versioning (`/api/v1/...` prefix) — cheap now, painful to retrofit later.
- Add pagination (`limit`/`offset` or cursor-based) to `get_all_users`/`get_all_courses`, with a consistent `{"items": [...], "total": ..., "limit": ..., "offset": ...}` envelope.
- Add filtering (e.g., courses by `instructor_id`) and sorting on list endpoints.
- Enrich OpenAPI docs: `summary`, `description`, and example values on routes/schemas so `/docs` reads like a real API reference, not an auto-generated stub.
- Normalize trailing-slash and naming conventions (`userRoutes.py`/`courseRoutes.py` → `user_routes.py`/`course_routes.py`) for PEP 8 consistency.

*Why it matters:* Pagination and versioning are two things almost every real API needs and almost every learning project skips — adding them is a strong, low-effort signal of production awareness.

---

## Phase 8 — Containerization & CI/CD
**Effort: Medium–Large | Depends on: Phase 2 (tests must exist to run in CI), Phase 4 (Postgres)**

- `Dockerfile` for the app, `docker-compose.yml` wiring the app + Postgres (+ Redis if you do Phase 9's caching).
- GitHub Actions workflow: install deps → lint (`ruff`) → run tests with coverage → build the Docker image on every PR.
- Optional but high-impact for a resume: deploy to a free/cheap host (Fly.io, Railway, Render) with a live URL and a CI badge in the README.

*Why it matters:* This is the "ship it" phase. A green CI badge and a live deployed URL turn this from "code on GitHub" into "a project someone can actually try," which is disproportionately persuasive in a portfolio.

---

## Phase 9 — Performance at Scale (stretch)
**Effort: Medium | Depends on: Phase 4 (async + relationships)**

- Use `selectinload`/`joinedload` for the instructor/enrollment relationships to eliminate N+1 queries once list endpoints join across tables.
- Add a caching layer (Redis) for a genuinely read-heavy endpoint (e.g., course catalog listing), with explicit cache invalidation on writes — the invalidation logic is the part worth demonstrating, not the cache-hit itself.
- Run a basic load test (`locust` or `hey`) against the async version and document before/after numbers vs. the original sync implementation. Concrete numbers in a README are far more convincing than a claim of "optimized for performance."

---

## Phase 10 — Pick One Differentiator (stretch)
**Effort: Medium | Pick 1, not all**

Depth over breadth — one of these done well is worth more than all of them done shallowly:

- **Full-text search** on courses using Postgres `tsvector`, once you're on Postgres.
- **WebSocket** endpoint for real-time enrollment notifications.
- **Audit log / soft deletes** — `deleted_at` instead of hard deletes, with an admin-only endpoint to view history.
- **API key auth** for a hypothetical machine client, alongside the existing JWT auth for humans — demonstrates you understand multiple auth schemes coexisting.

---

## Suggested Order of Attack

```
Phase 0 (hygiene)
   → Phase 1 (config)
      → Phase 2 (testing)         ← the real inflection point
         → Phase 3 (errors/API contract)
         → Phase 4 (domain model + async)
         → Phase 5 (auth hardening)
            → Phase 6 (observability)
            → Phase 7 (versioning/pagination)
               → Phase 8 (Docker/CI/CD)
                  → Phase 9 (performance, stretch)
                  → Phase 10 (one differentiator, stretch)
```

Phases 3–5 can be reordered relative to each other based on what you want to showcase first — but nothing after Phase 2 should be built without tests backing it, and nothing in Phase 5 (secrets, rate limiting) should be built before Phase 1's settings module exists to hold the configuration.
