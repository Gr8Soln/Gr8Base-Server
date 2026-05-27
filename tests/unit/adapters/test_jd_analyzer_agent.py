import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.adapters.ai.agents.jd_analyzer_agent import JDAnalyzerAgent, ParsedJobDescription
from app.domain.entities.job import JobDescription
from app.domain.exceptions.domain_exceptions import AIGenerationError


def _make_job() -> JobDescription:
    return JobDescription(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        raw_text="We need a Senior Backend Engineer with Python and FastAPI experience.",
    )


def _make_parsed_jd() -> ParsedJobDescription:
    return ParsedJobDescription(
        title="Senior Backend Engineer",
        company="TechCorp",
        location="Lagos, Nigeria",
        work_type="remote",
        role="Backend Engineer",
        seniority="Senior",
        domain="Fintech",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        preferred_skills=["Redis", "Docker"],
        soft_skills=["Communication", "Problem solving"],
        tools_and_technologies=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
        ats_keywords=["backend engineer", "python", "fastapi", "postgresql", "rest api"],
        hidden_signals=["Fast-paced environment", "Autonomous working style expected"],
        salary_min=80000,
        salary_max=120000,
    )


@pytest.mark.asyncio
async def test_jd_analyzer_populates_job_fields() -> None:
    job = _make_job()
    parsed = _make_parsed_jd()

    with patch(
        "app.adapters.ai.agents.jd_analyzer_agent.extract_structured",
        new=AsyncMock(return_value=parsed),
    ):
        agent = JDAnalyzerAgent()
        result = await agent.analyze(job.raw_text, job)

    assert result.title == "Senior Backend Engineer"
    assert result.seniority == "Senior"
    assert result.domain == "Fintech"
    assert "Python" in result.required_skills
    assert "Redis" in result.preferred_skills
    assert len(result.ats_keywords) == 5
    assert len(result.hidden_signals) == 2
    assert result.salary_min == 80000
    assert result.salary_max == 120000


@pytest.mark.asyncio
async def test_jd_analyzer_raises_on_llm_failure() -> None:
    job = _make_job()

    with patch(
        "app.adapters.ai.agents.jd_analyzer_agent.extract_structured",
        new=AsyncMock(side_effect=Exception("Timeout")),
    ):
        agent = JDAnalyzerAgent()
        with pytest.raises(AIGenerationError) as exc_info:
            await agent.analyze(job.raw_text, job)

    assert "jd_analyzer_agent" in str(exc_info.value)


@pytest.mark.asyncio
async def test_jd_analyzer_handles_minimal_jd() -> None:
    job = _make_job()
    minimal = ParsedJobDescription(
        title="",
        role="Backend Engineer",
        seniority="Mid-Level",
        required_skills=["Python"],
    )

    with patch(
        "app.adapters.ai.agents.jd_analyzer_agent.extract_structured",
        new=AsyncMock(return_value=minimal),
    ):
        agent = JDAnalyzerAgent()
        result = await agent.analyze("minimal jd", job)

    assert result.role == "Backend Engineer"
    assert result.required_skills == ["Python"]
    assert result.preferred_skills == []
    assert result.ats_keywords == []
