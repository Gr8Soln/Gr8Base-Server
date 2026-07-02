# Gr8Base Server — Database Schema

**Database**: PostgreSQL with pgvector extension
**ORM**: SQLAlchemy 2.0 async
**Migrations**: Alembic (async)
**Schema**: Public schema (default) — all tables in public schema currently; per-app schemas planned

---

## Tables Created (5 migration files)

### 1. `users` — Migration 0001

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| email | VARCHAR(320) | NOT NULL, UNIQUE, INDEX |
| hashed_password | VARCHAR(1024) | NOT NULL |
| full_name | VARCHAR(255) | NOT NULL, default '' |
| is_active | BOOLEAN | NOT NULL, default true |
| is_verified | BOOLEAN | NOT NULL, default false |
| is_superuser | BOOLEAN | NOT NULL, default false |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, server default now(), onupdate now() |

**Relationships**: Referenced by career_profiles, resumes, jobs, ats_scores via FK

---

### 2. `career_profiles` — Migration 0001

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| user_id | UUID | FK → users.id (CASCADE), UNIQUE, INDEX |
| full_name | VARCHAR(255) | NOT NULL |
| email | VARCHAR(320) | NOT NULL |
| headline | VARCHAR(500) | default '' |
| summary | TEXT | default '' |
| location | VARCHAR(255) | default '' |
| phone | VARCHAR(50) | default '' |
| linkedin_url | VARCHAR(500) | default '' |
| github_url | VARCHAR(500) | default '' |
| portfolio_url | VARCHAR(500) | default '' |
| years_of_experience | INTEGER | default 0 |
| target_roles | JSON | default [] |
| target_industries | JSON | default [] |
| target_salary_min | INTEGER | nullable |
| target_salary_max | INTEGER | nullable |
| preferred_work_type | VARCHAR(50) | default '' |
| writing_tone | VARCHAR(100) | default 'professional' |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, server default now(), onupdate now() |

---

### 3. `resumes` — Migration 0002

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| user_id | UUID | FK → users.id (CASCADE), NOT NULL, INDEX |
| file_url | VARCHAR(1000) | NOT NULL |
| file_name | VARCHAR(500) | NOT NULL |
| raw_text | TEXT | default '' |
| skills | JSON | default [] |
| experience | JSON | default [] |
| projects | JSON | default [] |
| education | JSON | default [] |
| certifications | JSON | default [] |
| languages | JSON | default [] |
| version | INTEGER | default 1 |
| label | VARCHAR(255) | default '' |
| strategy | VARCHAR(100) | nullable |
| parent_resume_id | UUID | FK → resumes.id (SET NULL), nullable |
| ats_score_snapshot | FLOAT | nullable |
| embedding | VECTOR(1536) | nullable (added in migration 0003) |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, server default now(), onupdate now() |

**Indexes**: `ix_resumes_embedding` (ivfflat, cosine_ops), `ix_resumes_user_id`

---

### 4. `jobs` — Migration 0004

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| user_id | UUID | FK → users.id (CASCADE), NOT NULL, INDEX |
| raw_text | TEXT | default '' |
| title | VARCHAR(500) | default '' |
| company | VARCHAR(500) | default '' |
| company_url | VARCHAR(1000) | default '' |
| location | VARCHAR(255) | default '' |
| work_type | VARCHAR(50) | default '' |
| role | VARCHAR(255) | default '' |
| seniority | VARCHAR(100) | default '' |
| domain | VARCHAR(255) | default '' |
| required_skills | JSON | default [] |
| preferred_skills | JSON | default [] |
| soft_skills | JSON | default [] |
| tools_and_technologies | JSON | default [] |
| ats_keywords | JSON | default [] |
| hidden_signals | JSON | default [] |
| salary_min | INTEGER | nullable |
| salary_max | INTEGER | nullable |
| embedding | VECTOR(1536) | nullable (added in migration 0003) |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, server default now(), onupdate now() |

**Indexes**: `ix_jobs_embedding` (ivfflat, cosine_ops), `ix_jobs_user_id`

---

### 5. `ats_scores` — Migration 0005

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| user_id | UUID | FK → users.id (CASCADE), NOT NULL, INDEX |
| resume_id | UUID | FK → resumes.id (CASCADE), NOT NULL, INDEX |
| job_id | UUID | FK → jobs.id (CASCADE), NOT NULL, INDEX |
| overall_score | FLOAT | NOT NULL |
| dimensions | JSON | default [] |
| dimension_breakdown | JSON | default {} |
| missing_keywords | JSON | default [] |
| weak_sections | JSON | default [] |
| recommendations | JSON | default [] |
| recruiter_critique | TEXT | default '' |
| is_ats_safe | BOOLEAN | default true |
| safety_issues | JSON | default [] |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() |

**Indexes**: `ix_ats_scores_user_id`, `ix_ats_scores_resume_id`, `ix_ats_scores_job_id`

---

## Missing Tables (models exist but no migration)

| Table | Model File | Migration |
|-------|-----------|-----------|
| applications | `application_model.py` (stub) | ❌ Missing |
| cover_letters | `cover_letter_model.py` (stub) | ❌ Missing |
| interview_prep | `interview_prep_model.py` (stub) | ❌ Missing |
| outreach | `outreach_model.py` (stub) | ❌ Missing |
| analytics | `analytics_model.py` (stub) | ❌ Missing |
| workflows | `workflow_model.py` (stub) | ❌ Missing |

---

## Migration History

| ID | Name | Up Revision | Down Revision |
|----|------|------------|---------------|
| 0001 | Initial users and careers profiles | `None` | — |
| 0002 | Add resumes table | `0001` | 0001 |
| 0003 | Add pgvector embeddings | `0002` | 0002 |
| 0004 | Add jobs table | `0003` | 0003 |
| 0005 | Add ats_scores table | `0004` | 0004 |

> **⚠️ Known Bug**: Migration 0003 (`add_pgvector_embeddings`) runs `ALTER TABLE jobs ADD COLUMN IF NOT EXISTS embedding vector(1536)` before migration 0004 creates the `jobs` table. This will fail at runtime with "relation 'jobs' does not exist" because `ADD COLUMN IF NOT EXISTS` only guards the column, not the table. To fix: either swap 0003 and 0004, or split the embedding columns across the two tables' respective migrations.

---

## ORM Notes
- All table inheritance uses `app.infrastructure.database.base.Base`
- Mixins: `TimestampMixin` (created_at, updated_at), `UUIDMixin` (id — uuid PK)
- Embedding columns use raw SQL via `op.execute()` rather than declarative ORM columns
- The `embedding` column on `ResumeModel` and `JobModel` is noted as a comment only — the actual column is created by migration 0003 via raw SQL
