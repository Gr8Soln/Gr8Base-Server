# Gr8Base Server — Agent System (LangGraph)

Two LangGraph workflows are implemented: **ATS Scoring** and **Resume Optimization**.
Three more (Cover Letter, Interview Prep, Workflow) exist only as empty stubs.

---

## 1. ATS Scoring Workflow

**File**: `app/adapters/ai/workflows/ats_scoring/`

### State: `ATSScoringState` (TypedDict)

| Field | Type | Reducer/Notes |
|-------|------|---------------|
| `user_id` | `str` | Input — set once |
| `resume_id` | `str` | Input — set once |
| `job_id` | `str` | Input — set once |
| `resume_data` | `dict` | Input — full resume JSON |
| `job_data` | `dict` | Input — full job JSON |
| `keyword_score` | `float` | 0.0–1.0, from keyword_match_node |
| `keyword_matches` | `list[str]` | Matched ATS keywords |
| `keyword_gaps` | `list[str]` | Missing ATS keywords |
| `semantic_score` | `float` | 0.0–1.0, from semantic_match_node |
| `semantic_gaps` | `list[str]` | Semantic alignment gaps |
| `technical_score` | `float` | 0.0–1.0, from technical_alignment_node |
| `technical_feedback` | `str` | Technical alignment feedback |
| `seniority_score` | `float` | 0.0–1.0, from heuristic (no LLM) |
| `impact_score` | `float` | 0.0–1.0, quantified impact ratio |
| `ats_safety_score` | `float` | 0.0–1.0, from ats_safety_node |
| `readability_score` | `float` | 0.0–1.0, from critique_node |
| `density_score` | `float` | 0.0–1.0, hardcoded 0.7 |
| `role_alignment_score` | `float` | Copied from semantic_score |
| `repetition_penalty` | `float` | 0.0 or 0.2, keyword stuffing |
| `is_ats_safe` | `bool` | From ats_safety_node |
| `safety_issues` | `list[str]` | ATS safety issues |
| `overall_score` | `float` | 0.0–100.0, weighted aggregate |
| `dimension_breakdown` | `dict` | Per-dimension scores/weights |
| `recommendations` | `list[str]` | Top 5 improvement suggestions |
| `missing_skills` | `list[str]` | Deduped missing skills (max 10) |
| `weak_sections` | `list[str]` | Top 3 red flags |
| `recruiter_critique` | `str` | Natural language critique |
| `errors` | `list[str]` | Error accumulation |

**No custom reducers** — default LangGraph overwrite semantics (each node returns the full update dict).

### Nodes

| # | Node | File | What it does | Reads from state | Writes to state |
|---|------|------|-------------|-----------------|-----------------|
| 1 | `keyword_match` | nodes.py:54 | LLM-based keyword match scoring (falls back to set intersection) | resume_data, job_data | keyword_score, keyword_matches, keyword_gaps |
| 2 | `semantic_match` | nodes.py:108 | LLM-based semantic alignment evaluation | resume_data, job_data | semantic_score, semantic_gaps |
| 3 | `technical_alignment` | nodes.py:140 | LLM-based tech stack alignment | resume_data, job_data | technical_score, technical_feedback, missing_skills |
| 4 | `seniority_alignment` | nodes.py:175 | Deterministic heuristic (YOE proxy based on job count) | resume_data, job_data | seniority_score |
| 5 | `impact_score` | nodes.py:202 | Ratio of quantified impact statements to total | resume_data | impact_score |
| 6 | `ats_safety` | nodes.py:222 | LLM-based ATS parser safety check | resume_data | ats_safety_score, is_ats_safe, safety_issues, repetition_penalty |
| 7 | `critique` | nodes.py:261 | LLM-based recruiter critique | resume_data, job_data, semantic_score | readability_score, density_score (0.7), role_alignment_score, weak_sections, recommendations, recruiter_critique |
| 8 | `aggregate_scores` | nodes.py:314 | Weighted average of all dimension scores | All score fields | overall_score, dimension_breakdown, missing_skills |

### Graph Wiring

```
keyword_match → semantic_match → technical_alignment → seniority_alignment → impact_score → ats_safety → critique → aggregate_scores → END
```

**Structure**: Purely sequential (no parallel branches, no conditionals, no interrupts).

**Weights** (in aggregate_scores_node):
- keyword_match: 25%
- semantic_match: 20%
- technical_alignment: 20%
- seniority_alignment: 10%
- quantified_impact: 10%
- ats_safety: 5%
- readability: 5%
- role_alignment: 5%

### Entry Point
`get_ats_scoring_workflow()` returns a compiled singleton graph.
Called from `ScoreResumeUseCase` (`app/application/use_cases/ats/score_resume.py`).

---

## 2. Resume Optimization Workflow

**File**: `app/adapters/ai/workflows/resume_optimization/`

### State: `ResumeOptimizationState` (TypedDict)

| Field | Type | Notes |
|-------|------|-------|
| `user_id` | `str` | Input |
| `resume_id` | `str` | Input |
| `job_id` | `str` | Input |
| `strategy_mode` | `str` | Input — e.g. "ats_aggressive" |
| `original_resume` | `dict` | Input — full resume JSON |
| `job_data` | `dict` | Input — full job JSON |
| `optimization_directives` | `dict` | From strategy_planning_node |
| `section_order` | `list[str]` | Default: summary, skills, experience, projects, education |
| `tone` | `str` | e.g. "professional" |
| `emphasis_keywords` | `list[str]` | Keywords to emphasize |
| `deemphasize` | `list[str]` | Sections/terms to de-emphasize |
| `optimized_experience` | `list[dict]` | Per-experience optimized bullets |
| `injected_skills` | `list[str]` | Skills added via keyword injection |
| `final_skills` | `list[str]` | Combined skills list |
| `optimized_resume` | `dict` | Fully assembled optimized resume |
| `pre_ats_score` | `float` | ATS score before optimization |
| `post_ats_score` | `float` | ATS score after optimization |
| `evaluation_passed` | `bool` | Passed threshold ≥60% |
| `iteration` | `int` | Current retry iteration (starts 0) |
| `max_iterations` | `int` | Default 2 |
| `critique_passed` | `bool` | Final critic approval |
| `critique_feedback` | `str` | Natural language feedback |
| `weak_points` | `list[str]` | From critic |
| `html_content` | `str` | Rendered HTML (planned) |
| `pdf_url` | `str` | Rendered PDF URL (planned) |
| `errors` | `list[str]` | Error accumulation |

### Nodes

| # | Node | File | What it does | Reads from | Writes to |
|---|------|------|-------------|-----------|----------|
| 1 | `strategy_planning` | nodes.py:67 | LLM plans optimization strategy | original_resume, job_data, strategy_mode | section_order, tone, emphasis_keywords, deemphasize, optimization_directives |
| 2 | `bullet_optimization` | nodes.py:102 | Per-experience LLM bullet rewrite | original_resume, job_data, emphasis_keywords, tone | optimized_experience (with fallback) |
| 3 | `keyword_injection` | nodes.py:143 | Deterministic — only injects proven keywords | original_resume, job_data | injected_skills, final_skills |
| 4 | `assemble_resume` | nodes.py:175 | Merges all node outputs into optimized_resume dict | All prior fields | optimized_resume |
| 5 | `ats_evaluation` | nodes.py:194 | Deterministic keyword coverage comparison | original_resume, optimized_resume, job_data | pre_ats_score, post_ats_score, evaluation_passed |
| 6 | `increment_iteration` | workflow.py:36 | Increments iteration counter | iteration | iteration+1 |
| 7 | `critic` | nodes.py:247 | LLM final quality check | optimized_resume, job_data | critique_passed, critique_feedback, weak_points |

### Graph Wiring

```
strategy_planning → bullet_optimization → keyword_injection → assemble_resume → ats_evaluation
                                                                                      │
                                                              ┌─────────────────────────┤
                                                              │ (evaluation_passed?)    │
                                                              │ no (retry)              │ yes (proceed)
                                                              ▼                         ▼
                                                    increment_iteration              critic → END
                                                              │
                                                              ▼
                                                    bullet_optimization (loop)
```

**Conditional Edge**: `_should_retry()` checks `evaluation_passed` and `iteration < max_iterations`.
- `"retry"` → loops back through `bullet_optimization`
- `"proceed"` → continues to `critic`

**Interrupts**: None. No `interrupt()` calls in either workflow.

### Entry Point
`get_resume_optimization_workflow()` returns a compiled singleton graph.
Called from `OptimizeResumeUseCase` (`app/application/use_cases/resume/optimize_resume.py`).

---

## 3. Cover Letter Workflow — STUB

**Files**: `app/adapters/ai/workflows/cover_letter/` — all 3 files empty.

## 4. Interview Prep Workflow — STUB

**Files**: `app/adapters/ai/workflows/interview_prep/` — all 3 files empty.

---

## Agent Tools

No explicit tools are registered on any agent node. All agents use the **Instructor client** (`app/infrastructure/llm/instructor_client.py`) which provides:
- Structured output enforcement via Pydantic `response_model`
- Automatic retries on schema validation failure (max 3)
- Multi-provider support (OpenAI + Anthropic via Instructor wrapper)

The **LLM Router** (`app/infrastructure/llm/llm_router.py`) provides:
- Primary/fallback model routing
- Automatic fallback on API errors
- LiteLLM integration for multi-provider

## Key Architectural Notes

1. **No LangGraph interrupt() calls** — neither workflow has human-in-the-loop points
2. **Singleton compiled graphs** — both workflows compile once and cache
3. **Fallback logic** — every LLM-powered node has a deterministic fallback in case of API error
4. **No parallel execution** — both graphs are purely sequential (the ATS scoring comment says "first three nodes run in parallel" but they actually run sequentially via add_edge())
5. **Every node returns `{"field": value}`** — partial state updates following LangGraph convention
