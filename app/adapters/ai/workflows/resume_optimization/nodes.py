"""
Resume Optimization Workflow Nodes.
Each node: takes state → returns partial state update dict.
"""
import copy

from pydantic import BaseModel, Field

from app.adapters.ai.prompts.resume.critic import (
    SYSTEM_PROMPT as CRITIC_SYSTEM,
)
from app.adapters.ai.prompts.resume.critic import (
    build_critic_prompt,
)
from app.adapters.ai.prompts.resume.optimize_bullets import (
    SYSTEM_PROMPT as BULLETS_SYSTEM,
)
from app.adapters.ai.prompts.resume.optimize_bullets import (
    build_bullet_prompt,
)
from app.adapters.ai.prompts.resume.strategy_planner import (
    SYSTEM_PROMPT as STRATEGY_SYSTEM,
)
from app.adapters.ai.prompts.resume.strategy_planner import (
    build_strategy_prompt,
)
from app.adapters.ai.workflows.resume_optimization.state import ResumeOptimizationState
from app.infrastructure.llm.instructor_client import extract_structured
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)

# ── Output schemas ────────────────────────────────────────────────────────────


class StrategyOutput(BaseModel):
    section_order: list[str] = Field(
        default_factory=lambda: [
            "summary", "skills", "experience", "projects", "education"
        ]
    )
    tone: str = "professional"
    emphasis_keywords: list[str] = Field(default_factory=list)
    deemphasize: list[str] = Field(default_factory=list)
    directives: dict = Field(default_factory=dict)


class BulletOptimizationOutput(BaseModel):
    optimized_bullets: list[str] = Field(
        default_factory=list,
        description="3-5 rewritten bullet points for this experience entry",
    )
    added_keywords: list[str] = Field(default_factory=list)


class CritiqueOutput(BaseModel):
    passes_six_second_scan: bool = True
    overall_quality: str = ""
    weak_points: list[str] = Field(default_factory=list)
    critical_issues: list[str] = Field(default_factory=list)
    approved: bool = True


# ── Nodes ─────────────────────────────────────────────────────────────────────


async def strategy_planning_node(state: ResumeOptimizationState) -> dict:
    logger.info("opt_node_strategy", resume_id=state["resume_id"])
    resume = state["original_resume"]
    job = state["job_data"]

    try:
        result: StrategyOutput = await extract_structured(
            response_model=StrategyOutput,
            messages=[
                {
                    "role": "user",
                    "content": build_strategy_prompt(resume, job, state["strategy_mode"]),
                }
            ],
            system=STRATEGY_SYSTEM,
            temperature=0.0,
        )
        return {
            "section_order": result.section_order,
            "tone": result.tone,
            "emphasis_keywords": result.emphasis_keywords,
            "deemphasize": result.deemphasize,
            "optimization_directives": result.directives,
        }
    except Exception as e:
        logger.error("strategy_planning_node_failed", error=str(e))
        return {
            "section_order": ["summary", "skills", "experience", "projects", "education"],
            "tone": "professional",
            "emphasis_keywords": job.get("ats_keywords", [])[:10],
            "deemphasize": [],
            "optimization_directives": {},
        }


async def bullet_optimization_node(state: ResumeOptimizationState) -> dict:
    logger.info("opt_node_bullets", resume_id=state["resume_id"])
    resume = state["original_resume"]
    job = state["job_data"]
    target_keywords = state.get("emphasis_keywords", job.get("ats_keywords", []))

    optimized_experience = []
    for exp in resume.get("experience", []):
        try:
            result: BulletOptimizationOutput = await extract_structured(
                response_model=BulletOptimizationOutput,
                messages=[
                    {
                        "role": "user",
                        "content": build_bullet_prompt(
                            experience=exp,
                            target_keywords=target_keywords,
                            job_role=job.get("role", ""),
                            tone=state.get("tone", "professional"),
                        ),
                    }
                ],
                system=BULLETS_SYSTEM,
                temperature=0.1,
            )
            exp_copy = copy.deepcopy(exp)
            exp_copy["optimized_bullets"] = result.optimized_bullets
            optimized_experience.append(exp_copy)
        except Exception as e:
            logger.warning(
                "bullet_optimization_failed",
                company=exp.get("company"),
                error=str(e),
            )
            exp_copy = copy.deepcopy(exp)
            exp_copy["optimized_bullets"] = _fallback_bullets(exp)
            optimized_experience.append(exp_copy)

    return {"optimized_experience": optimized_experience}


async def keyword_injection_node(state: ResumeOptimizationState) -> dict:
    """
    Safely injects missing ATS keywords into skills section.
    Only adds keywords that are genuinely supported by the resume's experience.
    Never fabricates skills.
    """
    logger.info("opt_node_keywords", resume_id=state["resume_id"])
    resume = state["original_resume"]
    job = state["job_data"]

    existing_skills = set(s.lower() for s in resume.get("skills", []))
    all_tech = set(
        t.lower()
        for exp in resume.get("experience", [])
        for t in exp.get("technologies", [])
    )
    proven_skills = existing_skills | all_tech

    # Only inject keywords we can prove exist in experience
    injectable = [
        kw for kw in job.get("ats_keywords", [])
        if kw.lower() in proven_skills and kw.lower() not in existing_skills
    ]

    final_skills = resume.get("skills", []) + injectable

    return {
        "injected_skills": injectable,
        "final_skills": final_skills,
    }


async def assemble_resume_node(state: ResumeOptimizationState) -> dict:
    """Assembles the final optimized resume dict from all node outputs."""
    logger.info("opt_node_assemble", resume_id=state["resume_id"])
    original = state["original_resume"]

    optimized = {
        "skills": state.get("final_skills", original.get("skills", [])),
        "experience": state.get("optimized_experience", original.get("experience", [])),
        "projects": original.get("projects", []),
        "education": original.get("education", []),
        "certifications": original.get("certifications", []),
        "languages": original.get("languages", []),
        "section_order": state.get("section_order", []),
        "tone": state.get("tone", "professional"),
    }

    return {"optimized_resume": optimized}


async def ats_evaluation_node(state: ResumeOptimizationState) -> dict:
    """
    Quick deterministic ATS evaluation of the optimized resume.
    Checks keyword coverage improvement vs original.
    """
    logger.info("opt_node_ats_eval", resume_id=state["resume_id"])
    original = state["original_resume"]
    optimized = state["optimized_resume"]
    job = state["job_data"]

    job_keywords = set(k.lower() for k in job.get("ats_keywords", []))
    if not job_keywords:
        return {"post_ats_score": 75.0, "evaluation_passed": True}

    def _keyword_coverage(resume_dict: dict) -> float:
        skills = set(s.lower() for s in resume_dict.get("skills", []))
        tech = set(
            t.lower()
            for exp in resume_dict.get("experience", [])
            for t in exp.get("technologies", [])
        )
        bullets_text = " ".join(
            b.lower()
            for exp in resume_dict.get("experience", [])
            for b in exp.get("optimized_bullets", [])
        )
        all_content = skills | tech | set(bullets_text.split())
        matched = job_keywords & all_content
        return len(matched) / len(job_keywords)

    pre_coverage = _keyword_coverage(original)
    post_coverage = _keyword_coverage(optimized)

    post_score = round(post_coverage * 100, 1)
    pre_score = round(pre_coverage * 100, 1)
    improved = post_coverage >= pre_coverage
    passed = post_score >= 60.0

    logger.info(
        "ats_eval_result",
        pre=pre_score,
        post=post_score,
        improved=improved,
        passed=passed,
    )

    return {
        "pre_ats_score": pre_score,
        "post_ats_score": post_score,
        "evaluation_passed": passed,
    }


async def critic_node(state: ResumeOptimizationState) -> dict:
    logger.info("opt_node_critic", resume_id=state["resume_id"])
    optimized = state["optimized_resume"]
    job = state["job_data"]

    try:
        result: CritiqueOutput = await extract_structured(
            response_model=CritiqueOutput,
            messages=[{"role": "user", "content": build_critic_prompt(optimized, job)}],
            system=CRITIC_SYSTEM,
            temperature=0.1,
        )
        feedback = (
            f"Quality: {result.overall_quality}\n"
            f"6-second scan: {'PASS' if result.passes_six_second_scan else 'FAIL'}\n"
            f"Critical issues: {'; '.join(result.critical_issues)}"
        )
        return {
            "critique_passed": result.approved,
            "critique_feedback": feedback,
            "weak_points": result.weak_points,
        }
    except Exception as e:
        logger.error("critic_node_failed", error=str(e))
        return {
            "critique_passed": True,
            "critique_feedback": "",
            "weak_points": [],
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fallback_bullets(exp: dict) -> list[str]:
    """Generate basic bullets from impact statements when LLM fails."""
    bullets = []
    for impact in exp.get("impact_statements", [])[:4]:
        result = impact.get("result", "")
        metric = impact.get("metric", "")
        solution = impact.get("solution", "")
        if solution:
            bullet = solution
            if metric:
                bullet += f", achieving {metric} improvement"
            elif result:
                bullet += f" — {result}"
            bullets.append(bullet)
    if not bullets and exp.get("description"):
        bullets.append(exp["description"][:120])
    return bullets or ["Contributed to team objectives and deliverables"]
