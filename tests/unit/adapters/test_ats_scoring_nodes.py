from unittest.mock import AsyncMock, patch

import pytest

from app.adapters.ai.workflows.ats_scoring.nodes import (
    KeywordMatchOutput,
    aggregate_scores_node,
    impact_score_node,
    keyword_match_node,
    seniority_alignment_node,
)
from app.adapters.ai.workflows.ats_scoring.state import ATSScoringState


def _base_state() -> ATSScoringState:
    return ATSScoringState(
        user_id="user-1",
        resume_id="resume-1",
        job_id="job-1",
        resume_data={
            "skills": ["Python", "FastAPI", "PostgreSQL", "Redis"],
            "experience": [
                {
                    "company": "Acme",
                    "role": "Backend Engineer",
                    "start_date": "2022-01",
                    "end_date": "2024-01",
                    "technologies": ["Python", "FastAPI"],
                    "impact_statements": [
                        {"problem": "P", "solution": "S", "result": "R", "metric": "40%"},
                        {"problem": "P2", "solution": "S2", "result": "R2", "metric": ""},
                    ],
                }
            ],
            "projects": [],
            "raw_text": "Senior Python backend engineer with FastAPI experience",
        },
        job_data={
            "title": "Senior Backend Engineer",
            "company": "TechCorp",
            "role": "Backend Engineer",
            "seniority": "Senior",
            "domain": "Fintech",
            "required_skills": ["Python", "FastAPI", "PostgreSQL"],
            "preferred_skills": ["Redis", "Docker"],
            "tools_and_technologies": ["Python", "FastAPI", "PostgreSQL"],
            "ats_keywords": ["python", "fastapi", "postgresql", "backend engineer"],
            "soft_skills": ["Communication"],
        },
        keyword_score=0.0,
        keyword_matches=[],
        keyword_gaps=[],
        semantic_score=0.0,
        semantic_gaps=[],
        technical_score=0.0,
        technical_feedback="",
        seniority_score=0.0,
        impact_score=0.0,
        ats_safety_score=0.0,
        readability_score=0.0,
        density_score=0.0,
        role_alignment_score=0.0,
        repetition_penalty=0.0,
        is_ats_safe=True,
        safety_issues=[],
        overall_score=0.0,
        dimension_breakdown={},
        recommendations=[],
        missing_skills=[],
        weak_sections=[],
        recruiter_critique="",
        errors=[],
    )


@pytest.mark.asyncio
async def test_keyword_match_node_llm_success() -> None:
    state = _base_state()
    mock_output = KeywordMatchOutput(
        score=0.85,
        matched_keywords=["python", "fastapi", "postgresql"],
        missing_keywords=["docker"],
    )

    with patch(
        "app.adapters.ai.workflows.ats_scoring.nodes.extract_structured",
        new=AsyncMock(return_value=mock_output),
    ):
        result = await keyword_match_node(state)

    assert result["keyword_score"] == 0.85
    assert "python" in result["keyword_matches"]
    assert "docker" in result["keyword_gaps"]


@pytest.mark.asyncio
async def test_keyword_match_node_fallback_on_llm_failure() -> None:
    """When LLM fails, falls back to deterministic set intersection."""
    state = _base_state()

    with patch(
        "app.adapters.ai.workflows.ats_scoring.nodes.extract_structured",
        new=AsyncMock(side_effect=Exception("LLM timeout")),
    ):
        result = await keyword_match_node(state)

    # Should not raise — graceful fallback
    assert "keyword_score" in result
    assert 0.0 <= result["keyword_score"] <= 1.0
    assert isinstance(result["keyword_matches"], list)


@pytest.mark.asyncio
async def test_seniority_alignment_senior_match() -> None:
    state = _base_state()
    # 1 job in experience = ~1.5 years proxy, but seniority is Senior
    result = await seniority_alignment_node(state)
    assert "seniority_score" in result
    assert 0.0 <= result["seniority_score"] <= 1.0


@pytest.mark.asyncio
async def test_impact_score_node_with_quantified_impacts() -> None:
    state = _base_state()
    # 1 quantified (40%), 1 not quantified → 0.5 ratio
    result = await impact_score_node(state)
    assert result["impact_score"] == 0.5


@pytest.mark.asyncio
async def test_impact_score_node_no_experience() -> None:
    state = _base_state()
    state["resume_data"]["experience"] = []
    result = await impact_score_node(state)
    assert result["impact_score"] == 0.2


@pytest.mark.asyncio
async def test_aggregate_scores_node_computes_weighted_total() -> None:
    state = _base_state()
    state.update({
        "keyword_score": 0.8,
        "semantic_score": 0.75,
        "technical_score": 0.9,
        "seniority_score": 0.7,
        "impact_score": 0.6,
        "ats_safety_score": 0.95,
        "readability_score": 0.8,
        "role_alignment_score": 0.75,
        "repetition_penalty": 0.0,
        "keyword_gaps": ["docker"],
        "missing_skills": ["kubernetes"],
    })

    result = await aggregate_scores_node(state)

    assert "overall_score" in result
    assert 0.0 <= result["overall_score"] <= 100.0
    assert "dimension_breakdown" in result
    # All 8 dimensions present
    assert len(result["dimension_breakdown"]) == 8
    # Missing skills deduplicated from both sources
    assert "docker" in result["missing_skills"]
    assert "kubernetes" in result["missing_skills"]


@pytest.mark.asyncio
async def test_aggregate_scores_applies_repetition_penalty() -> None:
    state = _base_state()
    state.update({
        "keyword_score": 1.0,
        "semantic_score": 1.0,
        "technical_score": 1.0,
        "seniority_score": 1.0,
        "impact_score": 1.0,
        "ats_safety_score": 1.0,
        "readability_score": 1.0,
        "role_alignment_score": 1.0,
        "repetition_penalty": 0.2,  # keyword stuffing penalty
        "keyword_gaps": [],
        "missing_skills": [],
    })

    result = await aggregate_scores_node(state)
    # Perfect scores minus 20% penalty → 80
    assert result["overall_score"] == 80.0
