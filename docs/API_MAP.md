# Gr8Base Server — API Map

All routes are prefixed with `/api/v1`. Only routes registered in `app/main.py` are exposed.

## Registered Routes (wired in main.py)

| Method | Path | Handler | File | Status |
|--------|------|---------|------|--------|
| GET | `/health` | `health_check` | main.py | ✅ Complete |
| POST | `/api/v1/auth/register` | `register` | auth_routes.py:29 | ✅ Complete |
| POST | `/api/v1/auth/login` | `login` | auth_routes.py:56 | ✅ Complete |
| POST | `/api/v1/auth/refresh` | `refresh` | auth_routes.py:72 | ✅ Complete |
| GET | `/api/v1/auth/me` | `me` | auth_routes.py:85 | ✅ Complete |
| GET | `/api/v1/profile/me` | `get_my_profile` | profile_routes.py:41 | ✅ Complete |
| PATCH | `/api/v1/profile/me` | `update_my_profile` | profile_routes.py:51 | ✅ Complete |
| POST | `/api/v1/resumes/upload` | `upload_resume` | resume_routes.py:110 | ✅ Complete |
| GET | `/api/v1/resumes` | `list_resumes` | resume_routes.py:151 | ✅ Complete |
| GET | `/api/v1/resumes/{resume_id}` | `get_resume` | resume_routes.py:160 | ✅ Complete |
| POST | `/api/v1/resumes/{resume_id}/optimize` | `optimize_resume` | resume_routes.py:170 | ✅ Complete |
| POST | `/api/v1/resumes/{resume_id}/pdf` | `generate_pdf` | resume_routes.py:199 | ✅ Complete |
| GET | `/api/v1/resumes/compare/{base_id}/{optimized_id}` | `compare_versions` | resume_routes.py:219 | ✅ Complete |
| POST | `/api/v1/resumes/{resume_id}/rollback` | `rollback_version` | resume_routes.py:240 | ✅ Complete |
| DELETE | `/api/v1/resumes/{resume_id}` | `delete_resume` | resume_routes.py:251 | ✅ Complete |
| POST | `/api/v1/jobs/analyze` | `analyze_job_description` | job_routes.py:47 | ✅ Complete |
| GET | `/api/v1/jobs` | `list_jobs` | job_routes.py:76 | ✅ Complete |
| GET | `/api/v1/jobs/{job_id}` | `get_job` | job_routes.py:86 | ✅ Complete |
| GET | `/api/v1/jobs/{job_id}/keywords` | `get_job_keywords` | job_routes.py:97 | ✅ Complete |
| DELETE | `/api/v1/jobs/{job_id}` | `delete_job` | job_routes.py:112 | ✅ Complete |
| POST | `/api/v1/ats/score` | `trigger_ats_score` | ats_routes.py:47 | ✅ Complete |
| GET | `/api/v1/ats/scores/{score_id}` | `get_ats_score` | ats_routes.py:64 | ✅ Complete |
| GET | `/api/v1/ats/scores` | `list_ats_scores` | ats_routes.py:75 | ✅ Complete |

**Total: 24 registered routes (including /health)**

## Stub Routes (files exist but NOT registered in main.py)

| Method | Path | Handler | File | Status |
|--------|------|---------|------|--------|
| (stub) | `/api/v1/applications/*` | — | application_routes.py | 🗂 Not imported in main.py |
| (stub) | `/api/v1/cover-letters/*` | — | cover_letter_routes.py | 🗂 Not imported in main.py |
| (stub) | `/api/v1/interview-prep/*` | — | interview_prep_routes.py | 🗂 Not imported in main.py |
| (stub) | `/api/v1/outreach/*` | — | outreach_routes.py | 🗂 Not imported in main.py |
| (stub) | `/api/v1/analytics/*` | — | analytics_routes.py | 🗂 Not imported in main.py |

### Auth routes not yet implemented
| Method | Path | Notes | Status |
|--------|------|-------|--------|
| POST | `/api/v1/auth/google` | Google OAuth callback | ❌ Missing route (use case exists) |
| POST | `/api/v1/auth/forgot-password` | Password reset flow | ❌ Missing entire |
| POST | `/api/v1/auth/reset-password` | Password reset flow | ❌ Missing entire |
| POST | `/api/v1/auth/invite` | Invite-only registration | ❌ Missing entire |
| POST | `/api/v1/auth/invite/accept` | Accept invite | ❌ Missing entire |
| POST | `/api/v1/auth/verify-email` | Email verification | ❌ Missing route (use case stub exists) |
