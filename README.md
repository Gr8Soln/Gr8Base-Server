# Caros

Premium AI-powered ATS optimization and job application intelligence platform.

## Architecture

Clean Architecture (Uncle Bob) with 4 layers:

```
app/
├── domain/          # Layer 1 — Entities, Enums, Value Objects, Exceptions
├── application/     # Layer 2 — Use Cases, Ports (abstract interfaces), DTOs
├── adapters/        # Layer 3 — API, Persistence, AI Agents, Storage, Queue, Renderer
└── infrastructure/  # Layer 4 — Config, DB, Redis, LLM, Observability, Security
```

Dependency rule: `infrastructure → adapters → application → domain`
Nothing in `domain` or `application` ever imports from `adapters` or `infrastructure`.

## Stack

- **FastAPI** — API framework
- **PostgreSQL + pgvector** — Database + vector search
- **Redis + Celery** — Async task queue
- **LangGraph** — AI workflow orchestration
- **LiteLLM + Instructor** — Multi-provider LLM with structured outputs
- **Cloudflare R2** — File storage
- **Langfuse** — LLM observability
- **WeasyPrint** — PDF rendering

## Quick Start

```bash
cp .env.example .env
# Fill in your API keys

make dev        # Start all services
make upgrade    # Run migrations
```

## Development

```bash
make test       # Run tests
make lint       # Lint with ruff
make typecheck  # Type check with mypy
make logs       # Tail app logs
```

## Implementation Phases

- Phase 0: Foundation ✅ (scaffold)
- Phase 1: Auth
- Phase 2: Career Profile
- Phase 3: Resume Parsing
- Phase 4: JD Intelligence
- Phase 5: Embeddings
- Phase 6: ATS Scoring
- Phase 7: Resume Optimization
- Phase 8: Versioning
- Phase 9: PDF Rendering (MVP complete)
- Phase 10: Cover Letters
- Phase 11: Cold Outreach
- Phase 12: Application Tracking
- Phase 13: Analytics
- Phase 14: Interview Prep
- Phase 15: Prompt Eval System
