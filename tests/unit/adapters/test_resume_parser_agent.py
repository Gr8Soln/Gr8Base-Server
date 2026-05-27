import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.adapters.ai.agents.resume_parser_agent import (
    ParsedEducation,
    ParsedExperience,
    ParsedImpact,
    ParsedProject,
    ParsedResume,
    ResumeParserAgent,
)
from app.domain.entities.resume import Resume
from app.domain.exceptions.domain_exceptions import AIGenerationError


def _make_resume() -> Resume:
    return Resume(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        file_url="https://r2.example.com/resume.pdf",
        file_name="resume.pdf",
        raw_text="",
    )


def _make_parsed_resume() -> ParsedResume:
    return ParsedResume(
        skills=["Python", "FastAPI", "PostgreSQL", "Redis", "LangGraph"],
        languages=["English", "Yoruba"],
        experience=[
            ParsedExperience(
                company="SoluTion Tech Hub",
                role="Senior Full Stack & AI Engineer",
                start_date="2022-01",
                end_date=None,
                is_current=True,
                location="Lagos, Nigeria",
                description="Building AI-powered backend systems",
                technologies=["Python", "FastAPI", "LangGraph"],
                impact_statements=[
                    ParsedImpact(
                        problem="Slow document processing pipeline",
                        solution="Implemented async Celery workers with Redis",
                        result="Reduced processing time by 60%",
                        metric="60%",
                    )
                ],
            )
        ],
        projects=[
            ParsedProject(
                name="NovaAcademy",
                description="RAG-powered learning platform",
                technologies=["Python", "Qdrant", "FastAPI"],
                url="https://github.com/Gr8Soln/nova",
                impact="Served 500+ students",
            )
        ],
        education=[
            ParsedEducation(
                institution="Obafemi Awolowo University",
                degree="B.Sc",
                field_of_study="Computer Science",
                start_year=2018,
                end_year=2022,
            )
        ],
        certifications=[],
    )


@pytest.mark.asyncio
async def test_parser_agent_populates_resume_fields() -> None:
    resume = _make_resume()
    parsed = _make_parsed_resume()

    with patch(
        "app.adapters.ai.agents.resume_parser_agent.extract_structured",
        new=AsyncMock(return_value=parsed),
    ):
        agent = ResumeParserAgent()
        result = await agent.parse("raw resume text", resume)

    assert result.skills == ["Python", "FastAPI", "PostgreSQL", "Redis", "LangGraph"]
    assert result.languages == ["English", "Yoruba"]
    assert len(result.experience) == 1
    assert result.experience[0].company == "SoluTion Tech Hub"
    assert result.experience[0].is_current is True
    assert result.experience[0].impact_statements[0].metric == "60%"
    assert len(result.projects) == 1
    assert result.projects[0].name == "NovaAcademy"
    assert len(result.education) == 1
    assert result.education[0].institution == "Obafemi Awolowo University"


@pytest.mark.asyncio
async def test_parser_agent_raises_on_llm_failure() -> None:
    resume = _make_resume()

    with patch(
        "app.adapters.ai.agents.resume_parser_agent.extract_structured",
        new=AsyncMock(side_effect=Exception("LLM timeout")),
    ):
        agent = ResumeParserAgent()
        with pytest.raises(AIGenerationError) as exc_info:
            await agent.parse("raw text", resume)

    assert "resume_parser_agent" in str(exc_info.value)
    assert "LLM timeout" in str(exc_info.value)


@pytest.mark.asyncio
async def test_parser_agent_handles_empty_sections() -> None:
    resume = _make_resume()
    empty_parsed = ParsedResume(
        skills=["Python"],
        experience=[],
        projects=[],
        education=[],
        certifications=[],
        languages=[],
    )

    with patch(
        "app.adapters.ai.agents.resume_parser_agent.extract_structured",
        new=AsyncMock(return_value=empty_parsed),
    ):
        agent = ResumeParserAgent()
        result = await agent.parse("minimal resume text", resume)

    assert result.skills == ["Python"]
    assert result.experience == []
    assert result.projects == []
