from unittest.mock import AsyncMock, patch

import pytest

from app.adapters.ai.workflows.resume_optimization.nodes import (
    CritiqueOutput,
    StrategyOutput,
    _fallback_bullets,
    assemble_resume_node,
    ats_evaluation_node,
    critic_node,
    keyword_injection_node,
    strategy_planning_node,
)
from app.adapters.ai.workflows.resume_optimization.state import ResumeOptimizationState


def _base_state() -> ResumeOptimizationState:
    return ResumeOptimizationState(
        user_id="u1", resume_id="r1", job_id="j1",
        strategy_mode="ats_aggressive",
        original_resume={
            "skills": ["Python", "FastAPI"],
            "experience": [
                {
                    "company": "Acme", "role": "Backend Engineer",
                    "start_date": "2022-01", "end_date": "2024-01",
                    "technologies": ["Python", "FastAPI", "Redis"],
                    "impact_statements": [
                        {"problem": "P", "solution": "Added caching",
                         "result": "Faster API", "metric": "40%"},
                    ],
                    "description": "Built APIs",
                    "optimized_bullets": [],
                }
            ],
            "projects": [], "education": [], "certifications": [], "languages": [],
            "raw_text": "Python FastAPI engineer",
        },
        job_data={
            "title": "Senior Backend Engineer", "company": "TechCorp",
            "role": "Backend Engineer", "seniority": "Senior",
            "domain": "Fintech",
            "required_skills": ["Python", "FastAPI", "Redis"],
            "preferred_skills": ["Docker"],
            "tools_and_technologies": ["Python", "FastAPI"],
            "ats_keywords": ["python", "fastapi", "redis", "backend engineer"],
            "hidden_signals": [],
        },
        optimization_directives={}, section_order=[], tone="professional",
        emphasis_keywords=[], deemphasize=[],
        optimized_experience=[], injected_skills=[], final_skills=[],
        optimized_resume={}, pre_ats_score=0.0, post_ats_score=0.0,
        evaluation_passed=False, iteration=0, max_iterations=2,
        critique_passed=False, critique_feedback="", weak_points=[],
        html_content="", pdf_url="", errors=[],
    )


@pytest.mark.asyncio
async def test_strategy_planning_node_success() -> None:
    state = _base_state()
    mock_output = StrategyOutput(
        section_order=["skills", "experience", "projects", "education"],
        tone="confident",
        emphasis_keywords=["python", "fastapi", "redis"],
        deemphasize=["unrelated_skill"],
        directives={"compress": True},
    )
    with patch(
        "app.adapters.ai.workflows.resume_optimization.nodes.extract_structured",
        new=AsyncMock(return_value=mock_output),
    ):
        result = await strategy_planning_node(state)

    assert result["tone"] == "confident"
    assert "python" in result["emphasis_keywords"]
    assert result["section_order"][0] == "skills"


@pytest.mark.asyncio
async def test_strategy_planning_node_fallback_on_failure() -> None:
    state = _base_state()
    with patch(
        "app.adapters.ai.workflows.resume_optimization.nodes.extract_structured",
        new=AsyncMock(side_effect=Exception("LLM timeout")),
    ):
        result = await strategy_planning_node(state)

    # Graceful fallback — never raises
    assert "section_order" in result
    assert "tone" in result
    assert len(result["section_order"]) > 0


@pytest.mark.asyncio
async def test_keyword_injection_only_injects_proven_skills() -> None:
    state = _base_state()
    # "redis" is in technologies but not in skills — injectable
    # "docker" is NOT in experience — must not be injected
    result = await keyword_injection_node(state)

    assert "redis" in [s.lower() for s in result["injected_skills"]]
    assert "docker" not in [s.lower() for s in result["injected_skills"]]
    assert "Python" in result["final_skills"]


@pytest.mark.asyncio
async def test_keyword_injection_no_duplicates() -> None:
    state = _base_state()
    # "python" already in skills — should not be duplicated
    result = await keyword_injection_node(state)
    final_lower = [s.lower() for s in result["final_skills"]]
    assert final_lower.count("python") == 1


@pytest.mark.asyncio
async def test_assemble_resume_uses_optimized_data() -> None:
    state = _base_state()
    state["final_skills"] = ["Python", "FastAPI", "Redis", "Docker"]
    state["optimized_experience"] = [{"company": "Acme", "role": "Engineer",
                                       "optimized_bullets": ["Built scalable APIs"]}]
    result = await assemble_resume_node(state)

    assert result["optimized_resume"]["skills"] == ["Python", "FastAPI", "Redis", "Docker"]
    assert len(result["optimized_resume"]["experience"]) == 1


@pytest.mark.asyncio
async def test_ats_evaluation_measures_keyword_coverage_improvement() -> None:
    state = _base_state()
    # Optimized resume has bullets mentioning keywords
    state["optimized_resume"] = {
        "skills": ["Python", "FastAPI", "Redis"],
        "experience": [
            {
                "technologies": ["Python", "FastAPI", "Redis"],
                "optimized_bullets": [
                    "Built python fastapi microservices with redis caching",
                    "Implemented backend engineer solutions",
                ],
            }
        ],
    }
    result = await ats_evaluation_node(state)

    assert "post_ats_score" in result
    assert 0.0 <= result["post_ats_score"] <= 100.0
    assert "evaluation_passed" in result


@pytest.mark.asyncio
async def test_critic_node_returns_feedback() -> None:
    state = _base_state()
    state["optimized_resume"] = {
        "skills": ["Python", "FastAPI"],
        "experience": [{"role": "Engineer", "company": "Acme", "optimized_bullets": []}],
    }
    mock_output = CritiqueOutput(
        passes_six_second_scan=True,
        overall_quality="Strong technical resume",
        weak_points=["Missing quantified impact in latest role"],
        critical_issues=[],
        approved=True,
    )
    with patch(
        "app.adapters.ai.workflows.resume_optimization.nodes.extract_structured",
        new=AsyncMock(return_value=mock_output),
    ):
        result = await critic_node(state)

    assert result["critique_passed"] is True
    assert "Strong technical resume" in result["critique_feedback"]
    assert len(result["weak_points"]) == 1


def test_fallback_bullets_generates_from_impacts() -> None:
    exp = {
        "impact_statements": [
            {"solution": "Implemented Redis caching", "metric": "40%", "result": ""},
            {"solution": "Refactored database queries", "metric": "", "result": "3x faster"},
        ]
    }
    bullets = _fallback_bullets(exp)
    assert len(bullets) >= 1
    assert any("Redis" in b for b in bullets)


def test_fallback_bullets_uses_description_when_no_impacts() -> None:
    exp = {"impact_statements": [], "description": "Led backend infrastructure migration"}
    bullets = _fallback_bullets(exp)
    assert len(bullets) == 1
    assert "infrastructure" in bullets[0]
