# Gr8Base — Server

## 1. Project Overview

Gr8Base (internally called "Caros") is a **premium AI-powered ATS optimization and job application intelligence platform**. It helps job seekers optimize their resumes for Applicant Tracking Systems (ATS), analyze job descriptions, generate cover letters, track applications, and prepare for interviews.

**Who uses it**: Personal OS — designed for a single user ("the Gr8Base user") with optional invite-only access for collaborators. No public registration.

**App modules**:
- **Core** — Foundation: FastAPI setup, config, database, auth, file storage, observability
- **Jobs** — Job description analysis, ATS keyword extraction, semantic matching
- **Resumes** — Upload, parse (AI), optimize (AI), versioning, PDF rendering
- **ATS** — Multi-dimensional scoring of resume-JD fit via LangGraph
- **Cover Letters** — AI generation (stub — not implemented)
- **Outreach** — Recruiter email, follow-up, thank-you note generation (stub — not implemented)
- **Application Tracking** — Pipeline management (stub — not implemented)
- **Interview Prep** — Question generation, prep packages (stub — not implemented)
- **Analytics** — Conversion rates, ATS trends (stub — not implemented)

---

## 2. Tech Stack

| Component | Technology | Version (if found) |
|-----------|-----------|-------------------|
| Language | Python | 3.12+ |
| API Framework | FastAPI | — |
| ORM | SQLAlchemy 2.0 (async) | — |
| Database | PostgreSQL + pgvector | — |
| Cache | Redis (async) | — |
| Task Queue | Celery (Redis broker) | — |
| AI Workflow | LangGraph | — |
| LLM Framework | LiteLLM + Instructor | — |
| Structured Output | Instructor (OpenAI + Anthropic) | — |
| Vector Search | pgvector (IVFFlat index) | — |
| File Storage | Cloudflare R2 (S3-compatible) | — |
| PDF Rendering | WeasyPrint | — |
| Auth | JWT (python-jose) + Google OAuth | — |
| Password Hashing | Argon2 (pwdlib) | — |
| Observability | Langfuse + Sentry + structlog | — |
| Container | Docker (implied by docker-compose reference, no files found) | — |

---

## 3. Architecture

**Clean Architecture (Robert C. Martin)** with 4 layers:

```
┌─────────────────────────────────────────────┐
│  Layer 1:  Domain     (entities, enums, VO) │  ← Innermost
│  Layer 2:  Application (use cases, ports)   │
│  Layer 3:  Adapters   (API, persistence, AI)│
│  Layer 4:  Infrastructure (config, DB, LLM) │  ← Outermost
└─────────────────────────────────────────────┘
```

**The Dependency Rule**: `infrastructure → adapters → application → domain`
- Nothing in `domain` or `application` ever imports from `adapters` or `infrastructure`
- All cross-layer communication goes through **ports** (abstract interfaces in `application/ports/`)
- All concrete implementations live in `adapters/`

**The One Rule That Must Never Be Broken**: Apps never import from each other. All shared logic lives in `shared/` or `apps/core/`. (Note: currently everything is under `app/` — there are no separate app packages.)

---

## 4. Folder Structure

```
app/
├── domain/             # Entities, Enums, Value Objects, Exceptions
├── application/        # Use Cases, Ports (interfaces), DTOs
├── adapters/           # API Routes, Persistence, AI, Queue, Storage, Renderer
└── infrastructure/     # Config, DB, Redis, LLM, Vector, Security, Observability
```

See `docs/STRUCTURE.md` for the full annotated tree.

---

## 5. App Modules

### Core (`app/`)
- **Purpose**: Application foundation — config, database, auth, security, observability
- **Domain entities**: User, CareerProfile
- **Use cases**: Register, Login (email/password), Google OAuth, Refresh Token
- **Key infrastructure**: JWT handler, Argon2 hashing, structlog logging, Sentry, Langfuse
- **API prefix**: `/api/v1/auth` (4 endpoints), `/api/v1/profile` (2 endpoints)
- **Status**: ✅ Auth is complete. Missing: forgot-password, reset-password, invite endpoints, email verification

### Jobs (`app/`)
- **Purpose**: Job description intelligence — parse, analyze, extract ATS keywords
- **Domain entities**: JobDescription, JobRequirement
- **Use cases**: Analyze JD (AI), Extract Keywords, Get Job
- **AI agent**: JDAnalyzerAgent (Instructor-based structured extraction)
- **API prefix**: `/api/v1/jobs` (5 endpoints)
- **Status**: ✅ Complete. Semantic matching agent is a stub.

### Resumes (`app/`)
- **Purpose**: Resume lifecycle — upload, AI parse, AI optimize, version control, PDF export
- **Domain entities**: Resume, WorkExperience, Project, Education, Certification, ImpactStatement
- **Use cases**: Upload, Parse, Optimize (LangGraph), Get, List Versions, Compare, Rollback, Generate PDF
- **AI agent**: ResumeParserAgent (Instructor-based)
- **LangGraph workflow**: ResumeOptimization (6 nodes + retry loop)
- **API prefix**: `/api/v1/resumes` (8 endpoints)
- **Status**: ✅ Complete (except search_similar stubbed out in repo)

### ATS Scoring (`app/`)
- **Purpose**: Multi-dimensional resume-JD fit scoring
- **Domain entities**: ATSScore, ScoreDimension
- **Use cases**: Score Resume (LangGraph), Get Score
- **LangGraph workflow**: ATSScoring (8 nodes, sequential)
- **API prefix**: `/api/v1/ats` (3 endpoints)
- **Status**: ✅ Complete

### Cover Letters — 🗂 NOT IMPLEMENTED
- Domain entity and use cases are empty stubs
- Scheme for cover_letter_tone enum is defined
- API routes exist but not registered

### Outreach — 🗂 NOT IMPLEMENTED
- All use cases and agents are empty stubs
- OutreachType enum defined
- API routes exist but not registered

### Application Tracking — 🗂 NOT IMPLEMENTED
- Domain entity (JobApplication) and enum (ApplicationStage) are defined
- All use cases are empty stubs
- No migration exists

### Interview Prep — 🗂 NOT IMPLEMENTED
- All use cases and agents are empty stubs
- API routes exist but not registered

### Analytics — 🗂 NOT IMPLEMENTED
- All use cases are empty stubs
- Celery beat schedule expects `aggregate_daily_analytics` but it's missing

---

## 6. Agent System (Jobs/ATS App)

### ATS Scoring Workflow
- **State**: ATSScoringState — 48 fields (inputs, dimension scores, outputs, errors)
- **8 nodes**: keyword_match → semantic_match → technical_alignment → seniority_alignment → impact_score → ats_safety → critique → aggregate_scores
- **Graph**: Fully sequential (no parallel branches, no conditionals, no interrupts)
- **Output**: 0–100 weighted score across 8 dimensions
- **File**: `app/adapters/ai/workflows/ats_scoring/`

### Resume Optimization Workflow
- **State**: ResumeOptimizationState — 50 fields (inputs, directives, optimized data, evaluation, control)
- **7 nodes**: strategy_planning → bullet_optimization → keyword_injection → assemble_resume → ats_evaluation → (retry loop → bullet_optimization OR proceed) → critic
- **Graph**: Sequential with conditional retry loop (up to 2 retries if ATS score < 60%)
- **No interrupts**: no human-in-the-loop points
- **File**: `app/adapters/ai/workflows/resume_optimization/`

### Key Patterns
- Every LLM-powered node has a deterministic fallback
- Singleton compiled graphs (compiled once, cached globally)
- Every node returns `{"field": value}` dict for state update
- No tools registered on any node — all use Instructor for structured output

See `docs/AGENTS.md` for full detail.

---

## 7. Database

- **PostgreSQL** with **pgvector** extension
- **ORM**: SQLAlchemy 2.0 async (asyncpg driver)
- **Migrations**: Alembic (async mode)
- **5 tables** created (5 migration files):
  - `users` — User accounts with hashed passwords
  - `career_profiles` — Extended career/profile data (1:1 with users)
  - `resumes` — Resume data with JSON structured fields + versioning
  - `jobs` — Job descriptions with analyzed fields
  - `ats_scores` — ATS scoring results per resume-job pair
- **Embeddings**: VECTOR(1536) columns on resumes + jobs with IVFFlat cosine similarity indexes
- **Missing tables**: applications, cover_letters, interview_prep, outreach, analytics, workflows (models exist but no migrations)

> **⚠️ Bug**: Migration 0003 references `jobs` table before it is created by migration 0004. Will fail at runtime.

See `docs/DATABASE.md` for full schema detail.

---

## 8. Auth

| Feature | Status | Details |
|---------|--------|---------|
| Email/password registration | ✅ Complete | POST `/api/v1/auth/register` |
| Email/password login | ✅ Complete | POST `/api/v1/auth/login` |
| JWT token refresh | ✅ Complete | POST `/api/v1/auth/refresh` |
| Get current user | ✅ Complete | GET `/api/v1/auth/me` |
| Google OAuth (use case) | ✅ Complete | `app/application/use_cases/auth/google_oauth.py` |
| Google OAuth (route) | ❌ Missing | No FastAPI route registered |
| Forgot password | ❌ Missing | Not started |
| Reset password | ❌ Missing | Not started |
| Email verification | 🗂 Stub | Use case exists but empty |
| Invite-only registration | ❌ Missing | Not started |

**Token format**: JWT, stored in localStorage on client. Access token (30min) + Refresh token (30 days).

---

## 9. Configuration

All configuration via `pydantic-settings` reading from `.env` file.

**Required env variables**:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async connection string |
| `SECRET_KEY` | App secret key (min 32 chars) |
| `JWT_SECRET` | JWT signing secret (min 32 chars) |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `R2_ACCOUNT_ID` | Cloudflare R2 account ID |
| `R2_ACCESS_KEY_ID` | R2 access key |
| `R2_SECRET_ACCESS_KEY` | R2 secret key |
| `R2_BUCKET_NAME` | R2 bucket name |
| `R2_PUBLIC_URL` | R2 public bucket URL |

**Optional env variables**:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment: development/staging/production |
| `DEBUG` | `false` | Enable debug mode |
| `DATABASE_POOL_SIZE` | 10 | Connection pool size |
| `DATABASE_MAX_OVERFLOW` | 20 | Max pool overflow |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | Celery result backend |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 30 | Refresh token TTL |
| `LLM_PRIMARY_MODEL` | `gpt-4o` | Primary LLM model |
| `LLM_FALLBACK_MODEL` | `claude-3-5-sonnet-20241022` | Fallback model |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `LANGFUSE_PUBLIC_KEY` | `""` | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | `""` | Langfuse secret key |
| `LANGFUSE_HOST` | cloud.langfuse.com | Langfuse host |
| `SENTRY_DSN` | `""` | Sentry DSN |
| `SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASSWORD/EMAIL_FROM` | `""` | Email config |
| `ENCRYPTION_KEY` | `""` | Fernet encryption key |

See `.env.example` for the full reference.

---

## 10. Implementation Status

**What is complete**: The foundation (infrastructure, config, database, auth, security) is fully built. The main API routes for auth, profile, resumes, jobs, and ATS scoring are wired and functional. The AI system has two fully implemented LangGraph workflows (ATS scoring with 8 nodes, resume optimization with 7 nodes + retry loop) and two working AI agents (resume parser, JD analyzer). File ingestion (PDF, DOCX, TXT), Cloudflare R2 storage, and PDF rendering (HTML → WeasyPrint) are implemented. The full Celery task queue with Beat scheduler is configured.

**What is partial**: The DI container is a stub (all wiring commented out). The `search_similar` method on both resume and job repositories returns an empty list. Migration 0003 has a bug (references jobs table before creation). The domain User entity is inconsistent with its usage (missing `hashed_password`, `is_superuser` fields that every consumer expects). The R2FileStorage uses synchronous boto3 with async def (non-yielding).

**What has not been started**: Cover letters, interview prep, cold outreach, application tracking, and analytics are entirely unimplemented — all use cases, agents, models, and schemas are empty files. Google OAuth has no route. Forgot/reset password, email verification, and invite flows are missing. Only 5 of ~12 planned database tables have migrations.

---

## 11. What to Build Next

Priority order:

### P0 — Fix bugs blocking deployment
1. **Fix migration ordering**: Swap migrations 0003 and 0004, or add table-creation guard to 0003
2. **Fix domain entity**: Add `hashed_password`, `is_superuser`, `is_active` fields to `User` domain entity (`domain/entities/user.py`) to match what every consumer expects
3. **Add missing `auth_provider` field**: The domain entity requires it but the mapper and use cases don't pass it

### P1 — Finish auth flows
4. **Add Google OAuth route**: Create `POST /api/v1/auth/google` in `auth_routes.py` calling the existing `GoogleAuthUseCase`
5. **Implement forgot/reset password**: End-to-end flow with email sending
6. **Add email verification**: Wire up `verify_email` use case

### P2 — Stub cleanup
7. **Wire remaining stub routers**: Cover letter, interview prep, outreach, analytics routers should be registered in `main.py` (even as TODOs)
8. **Initialize DI container**: Wire the `lagom` container with real implementations

### P3 — New module implementation
9. **Application tracking**: Create migration, repository, models, use cases, routes for `JobApplication` entity (entity + enum already defined)
10. **Cover letter generation**: Build on existing `cover_letter_tone` enum, create agent + workflow + routes
11. **Outreach generation**: Build on existing `outreach_type` enum

### P4 — Polish
12. **Fix `R2FileStorage`**: Use `aioboto3` or wrap sync calls in `run_in_executor`
13. **Implement `search_similar`**: Wire pgvector similarity search in resume and job repositories
14. **Add tests**: No test files exist anywhere in the project

---

## 12. Conventions & Rules

- **Language**: Python 3.12+ backend, TypeScript/React frontend (separate repo)
- **No cross-app imports**: Apps never import from each other; shared logic lives in the app root
- **Every LangGraph node returns `{"completed_tasks": ["node_name"]}`**: Actually, nodes return partial state updates matching the state TypedDict fields — they do NOT include a "completed_tasks" key
- **All repositories implement a defined interface (port)**: Every `Pg*Repository` class inherits from an abstract `*Repository` defined in `application/ports/repositories/`
- **Async everywhere**: asyncpg, SQLAlchemy async, httpx, aioredis
- **Instructor for all LLM calls**: Structured Pydantic output enforced by Instructor; every agent defines its own Pydantic output model
- **Fallback on LLM failure**: Every AI node has a deterministic fallback (set intersection, heuristic, or hardcoded value)
- **Seed UUIDs at the domain layer**: Domain entities use `field(default_factory=uuid.uuid4)`, not database-generated IDs
- **Dataclasses for domain entities**: All domain entities use `@dataclass` with `@field(default_factory=...)` for defaults
- **Pydantic BaseModel for schemas**: All API request/response models use Pydantic v2
- **Pydantic BaseModel for LLM output**: All structured LLM output models use Pydantic (nested in agent files)
- **Service layer pattern**: Use cases are instantiated in route handlers with explicit dependencies (no DI container yet)
- **Celery tasks create their own engine+sessions**: Tasks in the queue don't reuse the app's engine — they create async engines inline
- **Configuration is env-based**: `pydantic-settings` reads `.env` file, no hardcoded config
- **Versioned API**: All routes under `/api/v1/`
- **No test files exist**: No `tests/` directory or test configuration found
