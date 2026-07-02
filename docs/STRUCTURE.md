# Gr8Base Server — Full Directory Structure

```
gr8base/server/
├── AGENT.md                        ← Master context file (generated)
├── README.md                       ← Project overview, stack, quick start
├── start.sh                        ← Bash entrypoint: venv, .env, migrations, Celery, Uvicorn
│
├── .env.example                    ← All required env vars with defaults
├── .env                            ← Active env (gitignored)
├── .gitignore
├── .claude/
│   └── settings.local.json         ← Claude Code local settings
│
├── app/
│   ├── main.py                     ← FastAPI app factory: lifespan, CORS, router includes, /health
│   │
│   ├── domain/                     ═══════════════ LAYER 1 — DOMAIN ═══════════════
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── user.py             ← User, CareerProfile dataclasses (AuthProvider enum)
│   │   │   ├── resume.py           ← Resume, WorkExperience, Project, Education, Certification, ImpactStatement
│   │   │   ├── job.py              ← JobDescription, JobRequirement
│   │   │   ├── application.py      ← JobApplication, ApplicationNote (ApplicationStage enum)
│   │   │   ├── ats.py              ← ATSScore, ScoreDimension
│   │   │   ├── cover_letter.py     ← Empty (stub)
│   │   │   ├── interview_prep.py   ← Empty (stub)
│   │   │   ├── outreach.py         ← Empty (stub)
│   │   │   ├── analytics.py        ← Empty (stub)
│   │   │   ├── workflow.py         ← Empty (stub)
│   │   │   └── ...
│   │   ├── enums/
│   │   │   ├── application_stage.py  ← ApplicationStage: SAVED → GHOSTED
│   │   │   ├── cover_letter_tone.py  ← CoverLetterTone: FORMAL..EXECUTIVE
│   │   │   ├── outreach_type.py      ← OutreachType: RECRUITER_EMAIL..CONNECTION_REQUEST
│   │   │   ├── resume_strategy.py    ← ResumeStrategy: ATS_AGGRESSIVE..EUROPEAN_CV
│   │   │   └── workflow_status.py    ← WorkflowStatus: PENDING..RETRYING
│   │   ├── value_objects/
│   │   │   ├── ats_score.py        ← Empty
│   │   │   ├── email.py            ← Empty
│   │   │   └── impact_statement.py ← Empty
│   │   └── exceptions/
│   │       └── domain_exceptions.py  ← DomainException base + 7 subclasses
│   │
│   ├── application/                ═══════════════ LAYER 2 — APPLICATION ═══════════════
│   │   ├── __init__.py
│   │   ├── dto/
│   │   │   ├── user_dto.py         ← UserDTO, CareerProfileDTO
│   │   │   ├── resume_dto.py       ← ResumeDTO, WorkExperienceDTO, etc.
│   │   │   ├── job_dto.py          ← JobDTO
│   │   │   ├── application_dto.py  ← ApplicationDTO
│   │   │   ├── ats_dto.py          ← ATSScoreDTO, ScoreDimensionDTO
│   │   │   ├── cover_letter_dto.py ← CoverLetterDTO
│   │   │   ├── interview_prep_dto.py ← InterviewPrepDTO
│   │   │   ├── outreach_dto.py     ← OutreachDTO
│   │   │   └── analytics_dto.py    ← AnalyticsDTO
│   │   ├── ports/
│   │   │   ├── repositories/       ← Abstract repository interfaces
│   │   │   │   ├── user_repository.py       ← UserRepository + CareerProfileRepository
│   │   │   │   ├── resume_repository.py     ← ResumeRepository (incl. search_similar)
│   │   │   │   ├── job_repository.py        ← JobRepository (incl. search_similar)
│   │   │   │   ├── ats_repository.py        ← ATSRepository
│   │   │   │   ├── application_repository.py ← Empty
│   │   │   │   ├── cover_letter_repository.py ← Empty
│   │   │   │   ├── interview_prep_repository.py ← Empty
│   │   │   │   ├── outreach_repository.py   ← Empty
│   │   │   │   └── analytics_repository.py  ← Empty
│   │   │   ├── ai/                 ← Abstract AI service interfaces
│   │   │   │   ├── resume_parser_port.py     ← ResumeParserPort (✅)
│   │   │   │   ├── jd_analyzer_port.py       ← JDAnalyzerPort (✅)
│   │   │   │   ├── resume_optimizer_port.py  ← Empty
│   │   │   │   ├── ats_scorer_port.py        ← Empty
│   │   │   │   ├── cover_letter_port.py      ← Empty
│   │   │   │   ├── interview_prep_port.py    ← Empty
│   │   │   │   ├── outreach_port.py          ← Empty
│   │   │   │   └── embedding_port.py         ← Empty
│   │   │   ├── storage/
│   │   │   │   └── file_storage_port.py  ← FileStoragePort (upload, signed_url, delete)
│   │   │   ├── renderer/
│   │   │   │   ├── html_renderer_port.py ← Empty
│   │   │   │   └── pdf_renderer_port.py  ← PDFRendererPort (render_resume_pdf)
│   │   │   └── queue/
│   │   │       └── task_queue_port.py     ← Empty
│   │   └── use_cases/              ← Application business logic
│   │       ├── auth/
│   │       │   ├── register_user.py           ← RegisterUserUseCase (✅)
│   │       │   ├── authenticate_user.py       ← AuthenticateUserUseCase (✅)
│   │       │   ├── google_oauth.py            ← GoogleAuthUseCase (✅)
│   │       │   ├── refresh_token.py           ← RefreshTokenUseCase (✅)
│   │       │   └── verify_email.py            ← Empty
│   │       ├── profile/
│   │       │   ├── get_profile.py             ← GetProfileUseCase (✅)
│   │       │   ├── create_profile.py          ← CreateProfileUseCase (✅)
│   │       │   └── update_profile.py          ← UpdateProfileUseCase (✅)
│   │       ├── resume/
│   │       │   ├── upload_resume.py           ← UploadResumeUseCase (✅)
│   │       │   ├── parse_resume.py            ← ParseResumeUseCase (✅)
│   │       │   ├── optimize_resume.py         ← OptimizeResumeUseCase (partially calls Celery)
│   │       │   ├── get_resume.py              ← GetResumeUseCase (✅)
│   │       │   ├── list_resume_versions.py    ← ListResumeVersionsUseCase (✅)
│   │       │   ├── compare_resume_versions.py ← CompareResumeVersionsUseCase (✅)
│   │       │   ├── rollback_resume_version.py ← RollbackResumeVersionUseCase (✅)
│   │       │   └── generate_resume_pdf.py     ← GenerateResumePDFUseCase (✅)
│   │       ├── jobs/
│   │       │   ├── analyze_job_description.py ← AnalyzeJobDescriptionUseCase (✅)
│   │       │   ├── extract_keywords.py        ← ExtractKeywordsUseCase (✅)
│   │       │   └── get_job.py                 ← GetJobUseCase (✅)
│   │       ├── ats/
│   │       │   ├── score_resume.py            ← ScoreResumeUseCase (✅ — full LangGraph)
│   │       │   ├── get_ats_score.py           ← GetATSScoreUseCase (✅)
│   │       │   └── evaluate_ats_compatibility.py ← Empty
│   │       ├── applications/        ← All 5 use cases empty
│   │       ├── cover_letter/        ← All 3 use cases empty
│   │       ├── interview_prep/      ← Both use cases empty
│   │       ├── outreach/            ← All 3 use cases empty
│   │       └── analytics/           ← All 3 use cases empty
│   │
│   ├── adapters/                   ═══════════════ LAYER 3 — ADAPTERS ═══════════════
│   │   ├── api/                    ← FastAPI web layer
│   │   │   ├── routes/
│   │   │   │   ├── auth_routes.py          ← /register, /login, /refresh, /me (✅)
│   │   │   │   ├── profile_routes.py       ← /me GET + PATCH (✅)
│   │   │   │   ├── resume_routes.py        ← 8 endpoints (✅)
│   │   │   │   ├── job_routes.py           ← 5 endpoints (✅)
│   │   │   │   ├── ats_routes.py           ← 3 endpoints (✅)
│   │   │   │   ├── application_routes.py   ← Stub (5 lines)
│   │   │   │   ├── cover_letter_routes.py  ← Stub (5 lines)
│   │   │   │   ├── interview_prep_routes.py ← Stub (5 lines)
│   │   │   │   ├── outreach_routes.py      ← Stub (5 lines)
│   │   │   │   └── analytics_routes.py     ← Stub (5 lines)
│   │   │   ├── schemas/            ← Pydantic request/response models
│   │   │   │   ├── auth_schemas.py         ← LoginReq, RegisterReq, TokenResp, UserResp (✅)
│   │   │   │   ├── profile_schemas.py      ← ProfileResponse, UpdateProfileRequest (✅)
│   │   │   │   ├── resume_schemas.py       ← 12 models (✅)
│   │   │   │   ├── job_schemas.py          ← 3 models (✅)
│   │   │   │   ├── ats_schemas.py          ← 5 models (✅)
│   │   │   │   ├── common_schemas.py       ← HealthResp, TaskResp, PaginatedResp (✅)
│   │   │   │   ├── application_schemas.py  ← Empty
│   │   │   │   ├── cover_letter_schemas.py ← Empty
│   │   │   │   ├── outreach_schemas.py     ← Empty
│   │   │   │   └── analytics_schemas.py    ← Empty
│   │   │   ├── dependencies/
│   │   │   │   ├── auth.py                ← get_current_user JWT dependency (✅)
│   │   │   │   ├── injection.py           ← Empty (container wiring placeholder)
│   │   │   │   └── pagination.py          ← Empty
│   │   │   └── middleware/
│   │   │       ├── cors_middleware.py      ← CORS config (✅)
│   │   │       ├── error_middleware.py     ← DomainException → JSON handler (✅)
│   │   │       └── logging_middleware.py   ← Request/response logging (✅)
│   │   │
│   │   ├── persistence/            ← SQLAlchemy ORM + Repositories
│   │   │   ├── models/
│   │   │   │   ├── user_model.py              ← UserModel (users table)
│   │   │   │   ├── career_profile_model.py    ← CareerProfileModel (career_profiles table)
│   │   │   │   ├── resume_model.py            ← ResumeModel (resumes table)
│   │   │   │   ├── job_model.py               ← JobModel (jobs table)
│   │   │   │   ├── ats_model.py               ← ATSScoreModel (ats_scores table)
│   │   │   │   ├── application_model.py       ← Empty
│   │   │   │   ├── cover_letter_model.py      ← Empty
│   │   │   │   ├── interview_prep_model.py    ← Empty
│   │   │   │   ├── outreach_model.py          ← Empty
│   │   │   │   ├── analytics_model.py         ← Empty
│   │   │   │   └── workflow_model.py          ← Empty
│   │   │   ├── repositories/
│   │   │   │   ├── pg_user_repository.py          ← PgUserRepository + PgCareerProfileRepository (✅)
│   │   │   │   ├── pg_resume_repository.py        ← PgResumeRepository (✅, search_similar stubbed)
│   │   │   │   ├── pg_job_repository.py           ← PgJobRepository (✅, search_similar stubbed)
│   │   │   │   ├── pg_ats_repository.py           ← PgATSRepository (✅)
│   │   │   │   ├── pg_application_repository.py   ← Empty
│   │   │   │   ├── pg_cover_letter_repository.py  ← Empty
│   │   │   │   ├── pg_interview_prep_repository.py ← Empty
│   │   │   │   ├── pg_outreach_repository.py      ← Empty
│   │   │   │   └── pg_analytics_repository.py     ← Empty
│   │   │   └── mappers/
│   │   │       ├── user_mapper.py         ← User ↔ UserModel (✅)
│   │   │       ├── resume_mapper.py       ← Resume ↔ ResumeModel (✅)
│   │   │       ├── job_mapper.py          ← JobDesc ↔ JobModel (✅)
│   │   │       ├── ats_mapper.py          ← ATSScore ↔ ATSScoreModel (✅)
│   │   │       └── application_mapper.py  ← Empty
│   │   │
│   │   ├── ai/                      ← AI Agent Layer
│   │   │   ├── agents/
│   │   │   │   ├── resume_parser_agent.py     ← ResumeParserAgent (168 lines, ✅)
│   │   │   │   ├── jd_analyzer_agent.py       ← JDAnalyzerAgent (94 lines, ✅)
│   │   │   │   ├── ats_evaluator_agent.py     ← Empty
│   │   │   │   ├── bullet_optimizer_agent.py  ← Empty
│   │   │   │   ├── cover_letter_agent.py      ← Empty
│   │   │   │   ├── interview_prep_agent.py    ← Empty
│   │   │   │   ├── outreach_agent.py          ← Empty
│   │   │   │   ├── resume_critic_agent.py     ← Empty
│   │   │   │   ├── resume_strategy_agent.py   ← Empty
│   │   │   │   └── semantic_matching_agent.py ← Empty
│   │   │   ├── evaluators/          ← All 5 evaluators empty
│   │   │   ├── prompts/             ← LLM prompt templates
│   │   │   │   ├── resume/
│   │   │   │   │   ├── parse_resume.py       ← Parse prompt (✅)
│   │   │   │   │   ├── optimize_bullets.py   ← Bullet optimization prompt (✅)
│   │   │   │   │   ├── critic.py             ← Resume critic prompt (✅)
│   │   │   │   │   └── strategy_planner.py   ← Strategy planning prompt (✅)
│   │   │   │   ├── jd/
│   │   │   │   │   └── analyze_jd.py         ← JD analysis prompt (✅)
│   │   │   │   ├── scoring/
│   │   │   │   │   ├── ats_score.py          ← 5 scoring prompts (✅)
│   │   │   │   │   ├── keyword_extract.py    ← Empty
│   │   │   │   │   └── semantic_match.py     ← Empty
│   │   │   │   └── generation/
│   │   │   │       ├── cover_letter.py       ← Empty
│   │   │   │       ├── interview_questions.py ← Empty
│   │   │   │       └── outreach.py           ← Empty
│   │   │   └── workflows/           ← LangGraph state machines
│   │   │       ├── ats_scoring/
│   │   │       │   ├── state.py     ← ATSScoringState (48 fields)
│   │   │       │   ├── nodes.py     ← 9 nodes (keyword_match → aggregate)
│   │   │       │   └── workflow.py  ← Sequential graph wiring (✅)
│   │   │       ├── resume_optimization/
│   │   │       │   ├── state.py     ← ResumeOptimizationState (49 fields)
│   │   │       │   ├── nodes.py     ← 7 nodes with retry loop
│   │   │       │   └── workflow.py  ← Conditional retry graph (✅)
│   │   │       ├── cover_letter/    ← All 3 files empty
│   │   │       └── interview_prep/  ← All 3 files empty
│   │   │
│   │   ├── queue/                   ← Celery task definitions
│   │   │   ├── celery_task_queue.py ← Thin wrapper (empty stub)
│   │   │   └── tasks/
│   │   │       ├── resume_tasks.py       ← parse_resume_task (chains to embedding)
│   │   │       ├── scoring_tasks.py      ← score_resume_task
│   │   │       ├── generation_tasks.py   ← optimize_resume_task
│   │   │       ├── embedding_tasks.py    ← generate_resume_embedding, generate_job_embedding
│   │   │       ├── render_tasks.py       ← generate_pdf_task
│   │   │       └── analytics_tasks.py    ← Empty
│   │   │
│   │   ├── ingestion/               ← File text extraction
│   │   │   ├── ingestion_router.py  ← extract_text() dispatches by MIME type
│   │   │   ├── pdf_extractor.py     ← PyMuPDF extraction
│   │   │   ├── docx_extractor.py    ← python-docx extraction
│   │   │   └── txt_extractor.py     ← Raw text extraction
│   │   │
│   │   ├── renderer/                ← HTML + PDF generation
│   │   │   ├── html_renderer.py     ← Jinja2 → HTML resume renderer
│   │   │   ├── pdf_renderer.py      ← WeasyPrint HTML → PDF
│   │   │   └── templates/
│   │   │       ├── resume/
│   │   │       │   ├── base.html    ← Base template
│   │   │       │   ├── classic.html ← Classic style
│   │   │       │   ├── modern.html  ← Modern style
│   │   │       │   └── minimal.html ← Minimal style
│   │   │       └── email/
│   │   │           └── base.html    ← Email base template
│   │   │
│   │   └── storage/
│   │       └── r2_file_storage.py   ← Cloudflare R2 (S3-compatible) storage ✅
│   │
│   ├── infrastructure/              ═══════════════ LAYER 4 — INFRASTRUCTURE ═══════════════
│   │   ├── config/
│   │   │   ├── settings.py          ← Settings (pydantic-settings), env-based config
│   │   │   └── logging_config.py    ← Loguru + structlog config
│   │   ├── database/
│   │   │   ├── base.py              ← Base (declarative base), TimestampMixin, UUIDMixin
│   │   │   ├── connection.py        ← Async engine, session factory, get_db_session
│   │   │   └── migrations/
│   │   │       ├── env.py           ← Alembic async env
│   │   │       ├── script.py.mako   ← Migration template
│   │   │       └── versions/
│   │   │           ├── 0001_initial_users_and_profiles.py  ← users + career_profiles
│   │   │           ├── 0002_add_resumes_table.py            ← resumes table
│   │   │           ├── 0003_add_pgvector_embeddings.py      ← pgvector + embedding columns
│   │   │           ├── 0004_add_jobs_table.py                ← jobs table
│   │   │           └── 0005_add_ats_scores_table.py          ← ats_scores table
│   │   ├── llm/
│   │   │   ├── instructor_client.py  ← Structured output via Instructor (✅)
│   │   │   ├── llm_router.py         ← LiteLLM multi-provider routing (✅)
│   │   │   ├── anthropic_client.py   ← Empty
│   │   │   ├── openai_client.py      ← Empty
│   │   │   └── litellm_client.py     ← Empty
│   │   ├── redis/
│   │   │   ├── client.py           ← Async Redis client singleton
│   │   │   └── cache.py            ← cache_set/get/delete/delete_pattern
│   │   ├── vector/
│   │   │   ├── embedding_service.py ← OpenAI embedding generation
│   │   │   └── pgvector_client.py   ← Cosine similarity search helper
│   │   ├── queue/
│   │   │   ├── celery_app.py       ← Celery app definition
│   │   │   └── celery_config.py    ← Queue routing, beat schedule
│   │   ├── security/
│   │   │   ├── jwt_handler.py      ← JWT create/decode (✅)
│   │   │   ├── password_handler.py ← Argon2 hashing via pwdlib (✅)
│   │   │   └── encryption.py       ← Empty
│   │   ├── storage/
│   │   │   └── r2_client.py        ← Empty
│   │   ├── observability/
│   │   │   ├── structlog_setup.py  ← Structured logging (✅)
│   │   │   ├── sentry_setup.py     ← Sentry DSN init
│   │   │   └── langfuse_client.py  ← Langfuse singleton
│   │   └── container.py           ← DI container (stub — all wiring commented out)
│   │
│   └── adapters/__init__.py
│
├── scripts/                        ← (referenced by start.sh)
│   └── setup_super_account.py      ← (optional, for admin bootstrap)
│
└── logs/                           ← Runtime logs directory
```
