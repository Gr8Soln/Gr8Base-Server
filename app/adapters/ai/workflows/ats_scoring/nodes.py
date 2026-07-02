"""
ATS Scoring Workflow Nodes.
Each node is a pure function: takes state, returns partial state update.
"""
from pydantic import BaseModel, Field

from app.adapters.ai.workflows.ats_scoring.state import ATSScoringState
from app.infrastructure.llm.instructor_client import extract_structured
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


# ── Output schemas ────────────────────────────────────────────────────────────

class KeywordMatchOutput(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)


class SemanticMatchOutput(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    semantic_gaps: list[str] = Field(default_factory=list)
    alignment_notes: str = ""


class TechnicalAlignmentOutput(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    matched_technologies: list[str] = Field(default_factory=list)
    missing_technologies: list[str] = Field(default_factory=list)
    feedback: str = ""


class ATSSafetyOutput(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    is_safe: bool = True
    issues: list[str] = Field(default_factory=list)
    has_keyword_stuffing: bool = False


class CritiqueOutput(BaseModel):
    first_impression: str = ""
    relevance_assessment: str = ""
    impact_strength: str = ""
    red_flags: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    overall_critique: str = ""
    readability_score: float = Field(ge=0.0, le=1.0, default=0.7)


# ── Node functions ────────────────────────────────────────────────────────────

async def keyword_match_node(state: ATSScoringState) -> dict:
    logger.info("ats_node_keyword_match", resume_id=state["resume_id"])
    resume = state["resume_data"]
    job = state["job_data"]

    resume_skills = set(s.lower() for s in resume.get("skills", []))
    experience_techs = set(
        t.lower()
        for exp in resume.get("experience", [])
        for t in exp.get("technologies", [])
    )
    all_resume_keywords = resume_skills | experience_techs

    ats_keywords = [k.lower() for k in job.get("ats_keywords", [])]
    required_skills = [s.lower() for s in job.get("required_skills", [])]
    all_job_keywords = list(dict.fromkeys(ats_keywords + required_skills))

    if not all_job_keywords:
        return {
            "keyword_score": 0.5,
            "keyword_matches": [],
            "keyword_gaps": [],
        }

    try:
        prompt = f"""Resume keywords: {list(all_resume_keywords)}
Job ATS keywords: {all_job_keywords}
Required skills: {required_skills}

Score the keyword match. Focus on exact and near-exact matches."""

        result: KeywordMatchOutput = await extract_structured(
            response_model=KeywordMatchOutput,
            messages=[{"role": "user", "content": prompt}],
            system="You are an ATS keyword matching specialist. Return valid JSON only.",
            temperature=0.0,
        )
        return {
            "keyword_score": result.score,
            "keyword_matches": result.matched_keywords,
            "keyword_gaps": result.missing_keywords,
        }
    except Exception as e:
        logger.error("keyword_match_node_failed", error=str(e))
        # Fallback: deterministic set intersection
        matched = [k for k in all_job_keywords if k in all_resume_keywords]
        score = len(matched) / max(len(all_job_keywords), 1)
        return {
            "keyword_score": round(score, 2),
            "keyword_matches": matched,
            "keyword_gaps": [k for k in all_job_keywords if k not in all_resume_keywords],
        }


async def semantic_match_node(state: ATSScoringState) -> dict:
    logger.info("ats_node_semantic_match", resume_id=state["resume_id"])
    resume = state["resume_data"]
    job = state["job_data"]

    resume_summary = _build_resume_summary(resume)
    job_summary = _build_job_summary(job)

    try:
        prompt = f"""RESUME SUMMARY:
{resume_summary}

JOB REQUIREMENTS:
{job_summary}

Evaluate semantic alignment — conceptual fit beyond keyword matching."""

        result: SemanticMatchOutput = await extract_structured(
            response_model=SemanticMatchOutput,
            messages=[{"role": "user", "content": prompt}],
            system="You are a semantic relevance expert. Return valid JSON only.",
            temperature=0.0,
        )
        return {
            "semantic_score": result.score,
            "semantic_gaps": result.semantic_gaps,
        }
    except Exception as e:
        logger.error("semantic_match_node_failed", error=str(e))
        return {"semantic_score": 0.5, "semantic_gaps": []}


async def technical_alignment_node(state: ATSScoringState) -> dict:
    logger.info("ats_node_technical_alignment", resume_id=state["resume_id"])
    resume = state["resume_data"]
    job = state["job_data"]

    resume_tech = list(set(
        t for exp in resume.get("experience", [])
        for t in exp.get("technologies", [])
    ) | set(resume.get("skills", [])))

    job_tech = job.get("tools_and_technologies", []) + job.get("required_skills", [])

    try:
        prompt = f"""Candidate technologies: {resume_tech}
Job required technologies: {job_tech}
Preferred technologies: {job.get('preferred_skills', [])}

Evaluate technical stack alignment."""

        result: TechnicalAlignmentOutput = await extract_structured(
            response_model=TechnicalAlignmentOutput,
            messages=[{"role": "user", "content": prompt}],
            system="You are a technical hiring expert. Return valid JSON only.",
            temperature=0.0,
        )
        return {
            "technical_score": result.score,
            "technical_feedback": result.feedback,
            "missing_skills": result.missing_technologies,
        }
    except Exception as e:
        logger.error("technical_alignment_node_failed", error=str(e))
        return {"technical_score": 0.5, "technical_feedback": "", "missing_skills": []}


async def seniority_alignment_node(state: ATSScoringState) -> dict:
    logger.info("ats_node_seniority", resume_id=state["resume_id"])
    resume = state["resume_data"]
    job = state["job_data"]

    exp_count = len(resume.get("experience", []))
    job_seniority = job.get("seniority", "").lower()

    # Deterministic heuristic — no LLM call needed for this dimension
    seniority_map = {
        "junior": (0, 2),
        "mid-level": (2, 5),
        "mid": (2, 5),
        "senior": (5, 10),
        "staff": (7, 15),
        "principal": (10, 20),
        "lead": (5, 15),
    }

    expected_range = seniority_map.get(job_seniority, (0, 20))
    years_proxy = min(exp_count * 1.5, 15)  # rough proxy from job count
    in_range = expected_range[0] <= years_proxy <= expected_range[1]
    score = 1.0 if in_range else (0.6 if abs(years_proxy - expected_range[0]) <= 2 else 0.3)

    return {"seniority_score": round(score, 2)}


async def impact_score_node(state: ATSScoringState) -> dict:
    logger.info("ats_node_impact", resume_id=state["resume_id"])
    resume = state["resume_data"]

    all_impacts = [
        impact
        for exp in resume.get("experience", [])
        for impact in exp.get("impact_statements", [])
    ]

    quantified = [i for i in all_impacts if i.get("metric", "").strip()]
    total = len(all_impacts)
    score = (len(quantified) / max(total, 1)) if total > 0 else 0.3
    # Bonus for having any impacts at all
    if total == 0:
        score = 0.2

    return {"impact_score": round(min(score, 1.0), 2)}


async def ats_safety_node(state: ATSScoringState) -> dict:
    logger.info("ats_node_safety", resume_id=state["resume_id"])
    resume = state["resume_data"]

    raw_text = resume.get("raw_text", "")
    skills = resume.get("skills", [])

    try:
        prompt = f"""Resume raw text (first 3000 chars):
{raw_text[:3000]}

Skills list: {skills[:30]}

Evaluate ATS parser safety. Check for formatting issues, keyword stuffing,
non-standard section headers, or anything that would confuse ATS parsers."""

        result: ATSSafetyOutput = await extract_structured(
            response_model=ATSSafetyOutput,
            messages=[{"role": "user", "content": prompt}],
            system="You are an ATS systems expert. Return valid JSON only.",
            temperature=0.0,
        )
        penalty = 0.2 if result.has_keyword_stuffing else 0.0
        return {
            "ats_safety_score": round(max(result.score - penalty, 0.0), 2),
            "is_ats_safe": result.is_safe,
            "safety_issues": result.issues,
            "repetition_penalty": penalty,
        }
    except Exception as e:
        logger.error("ats_safety_node_failed", error=str(e))
        return {
            "ats_safety_score": 0.7,
            "is_ats_safe": True,
            "safety_issues": [],
            "repetition_penalty": 0.0,
        }


async def critique_node(state: ATSScoringState) -> dict:
    logger.info("ats_node_critique", resume_id=state["resume_id"])
    resume = state["resume_data"]
    job = state["job_data"]

    resume_summary = _build_resume_summary(resume)

    try:
        prompt = f"""RESUME:
{resume_summary}

TARGET ROLE: {job.get('title', '')} at {job.get('company', '')}
SENIORITY: {job.get('seniority', '')}
DOMAIN: {job.get('domain', '')}

Review this resume as a senior recruiter would. Be honest and specific."""

        result: CritiqueOutput = await extract_structured(
            response_model=CritiqueOutput,
            messages=[{"role": "user", "content": prompt}],
            system="You are an experienced senior recruiter. Be direct and specific. JSON only.",
            temperature=0.1,
        )

        weak_sections = result.red_flags[:3]
        recommendations = result.improvement_suggestions[:5]
        critique_text = (
            f"{result.first_impression}\n\n"
            f"Relevance: {result.relevance_assessment}\n\n"
            f"Impact: {result.impact_strength}\n\n"
            f"{result.overall_critique}"
        ).strip()

        return {
            "readability_score": result.readability_score,
            "density_score": 0.7,  # placeholder — computed from resume length heuristic
            "role_alignment_score": state.get("semantic_score", 0.5),
            "weak_sections": weak_sections,
            "recommendations": recommendations,
            "recruiter_critique": critique_text,
        }
    except Exception as e:
        logger.error("critique_node_failed", error=str(e))
        return {
            "readability_score": 0.7,
            "density_score": 0.7,
            "role_alignment_score": 0.5,
            "weak_sections": [],
            "recommendations": [],
            "recruiter_critique": "",
        }


async def aggregate_scores_node(state: ATSScoringState) -> dict:
    """Final node — computes weighted overall score and builds dimension breakdown."""
    logger.info("ats_node_aggregate", resume_id=state["resume_id"])

    weights = {
        "keyword_match": 0.25,
        "semantic_match": 0.20,
        "technical_alignment": 0.20,
        "seniority_alignment": 0.10,
        "quantified_impact": 0.10,
        "ats_safety": 0.05,
        "readability": 0.05,
        "role_alignment": 0.05,
    }

    scores = {
        "keyword_match": state.get("keyword_score", 0.0),
        "semantic_match": state.get("semantic_score", 0.0),
        "technical_alignment": state.get("technical_score", 0.0),
        "seniority_alignment": state.get("seniority_score", 0.0),
        "quantified_impact": state.get("impact_score", 0.0),
        "ats_safety": state.get("ats_safety_score", 0.0),
        "readability": state.get("readability_score", 0.0),
        "role_alignment": state.get("role_alignment_score", 0.0),
    }

    # Apply repetition penalty to overall
    penalty = state.get("repetition_penalty", 0.0)
    weighted = sum(scores[k] * weights[k] for k in weights)
    overall = round(max((weighted - penalty) * 100, 0.0), 1)

    dimension_breakdown = {
        dim: {
            "score": round(scores[dim] * 100, 1),
            "weight": weights[dim],
            "weighted_contribution": round(scores[dim] * weights[dim] * 100, 1),
        }
        for dim in weights
    }

    # Combine missing skills from keyword + technical nodes
    missing = list(dict.fromkeys(
        state.get("keyword_gaps", []) + state.get("missing_skills", [])
    ))[:10]

    return {
        "overall_score": overall,
        "dimension_breakdown": dimension_breakdown,
        "missing_skills": missing,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_resume_summary(resume: dict) -> str:
    parts = [f"Skills: {', '.join(resume.get('skills', [])[:20])}"]
    for exp in resume.get("experience", [])[:3]:
        impacts = [i.get("result", "") for i in exp.get("impact_statements", [])[:2]]
        parts.append(
            f"- {exp.get('role')} at {exp.get('company')} "
            f"({exp.get('start_date')}–{exp.get('end_date', 'Present')}): "
            f"{'; '.join(impacts)}"
        )
    for proj in resume.get("projects", [])[:2]:
        parts.append(f"- Project: {proj.get('name')}: {proj.get('description', '')[:100]}")
    return "\n".join(parts)


def _build_job_summary(job: dict) -> str:
    return (
        f"Role: {job.get('role')} ({job.get('seniority')})\n"
        f"Domain: {job.get('domain')}\n"
        f"Required: {', '.join(job.get('required_skills', []))}\n"
        f"Preferred: {', '.join(job.get('preferred_skills', []))}\n"
        f"ATS Keywords: {', '.join(job.get('ats_keywords', []))}"
    )
