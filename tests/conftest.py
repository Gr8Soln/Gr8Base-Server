"""Shared test fixtures and configuration."""

import uuid
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.entities.award import Award
from app.domain.entities.blog import Blog
from app.domain.entities.career_profile import CareerProfile
from app.domain.entities.certification import Certification
from app.domain.entities.education import Education
from app.domain.entities.experience import ImpactStatement, WorkExperience
from app.domain.entities.language import Language
from app.domain.entities.project import Project
from app.domain.entities.publication import Publication
from app.domain.entities.skill import Skill
from app.domain.entities.technology import Technology
from app.domain.enums.employment_type import EmploymentType
from app.domain.enums.skill_category import SkillCategory
from app.infrastructure.database.base import Base


@pytest.fixture
def sample_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def sample_career_profile(sample_user_id: uuid.UUID) -> CareerProfile:
    return CareerProfile(
        user_id=sample_user_id,
        full_name="Jane Doe",
        email="jane@example.com",
        headline="Senior Software Engineer",
        summary="Experienced engineer with 10 years in backend systems.",
        location="San Francisco, CA",
        phone="+1-555-0123",
        linkedin_url="https://linkedin.com/in/janedoe",
        github_url="https://github.com/janedoe",
        portfolio_url="https://janedoe.dev",
        website="https://janedoe.dev",
        years_of_experience=10,
        target_roles=["Staff Engineer", "Engineering Manager"],
        target_industries=["SaaS", "Fintech"],
    )


@pytest.fixture
def sample_experience(sample_user_id: uuid.UUID) -> WorkExperience:
    return WorkExperience(
        user_id=sample_user_id,
        company="Acme Corp",
        role="Senior Software Engineer",
        start_date="2020-01",
        end_date=None,
        is_current=True,
        location="San Francisco, CA",
        description="Led backend architecture for payment platform.",
        employment_type=EmploymentType.FULL_TIME,
        industry="Fintech",
        company_website="https://acme.com",
        responsibilities=["Designed microservices architecture", "Led team of 5 engineers"],
        achievements=["Reduced latency by 40%", "Saved $2M annually"],
        technologies=["Python", "FastAPI", "PostgreSQL", "Kubernetes"],
        impact_statements=[
            ImpactStatement(
                problem="High latency in payment processing",
                solution="Redesigned async pipeline",
                result="40% latency reduction",
                metric="40%",
            )
        ],
    )


@pytest.fixture
def sample_project(sample_user_id: uuid.UUID) -> Project:
    return Project(
        user_id=sample_user_id,
        name="Payment Gateway",
        description="Real-time payment processing system",
        role="Lead Architect",
        technologies=["Python", "FastAPI", "Redis", "PostgreSQL"],
        responsibilities=["Architected solution", "Implemented core services"],
        repository="https://github.com/janedoe/payment-gateway",
        demo_url="https://demo.example.com",
        duration="6 months",
        impact="Processed $100M in transactions",
    )


@pytest.fixture
def sample_skill(sample_user_id: uuid.UUID) -> Skill:
    return Skill(
        user_id=sample_user_id,
        name="Python",
        category=SkillCategory.TECHNICAL,
        proficiency="expert",
        years_of_experience=8.0,
    )


@pytest.fixture
def sample_technology(sample_user_id: uuid.UUID) -> Technology:
    return Technology(
        user_id=sample_user_id,
        name="Docker",
        category=SkillCategory.TOOL,
        proficiency="advanced",
    )


@pytest.fixture
def sample_education(sample_user_id: uuid.UUID) -> Education:
    return Education(
        user_id=sample_user_id,
        institution="Stanford University",
        degree="B.S. Computer Science",
        field_of_study="Computer Science",
        start_year=2010,
        end_year=2014,
        gpa=3.8,
        honors="Magna Cum Laude",
    )


@pytest.fixture
def sample_certification(sample_user_id: uuid.UUID) -> Certification:
    return Certification(
        user_id=sample_user_id,
        name="AWS Solutions Architect",
        issuer="Amazon Web Services",
        issue_date="2022-06",
        credential_url="https://aws.amazon.com/verify/abc123",
        credential_id="ABC123",
    )


@pytest.fixture
def sample_award(sample_user_id: uuid.UUID) -> Award:
    return Award(
        user_id=sample_user_id,
        name="Engineer of the Year",
        issuer="Acme Corp",
        date="2023",
        description="For outstanding contributions to the payment platform.",
    )


@pytest.fixture
def sample_publication(sample_user_id: uuid.UUID) -> Publication:
    return Publication(
        user_id=sample_user_id,
        title="Scaling Payment Systems",
        publisher="Tech Blog",
        date="2023-05",
        url="https://techblog.com/scaling-payments",
        description="How we scaled our payment system to handle 1M TPS.",
    )


@pytest.fixture
def sample_blog(sample_user_id: uuid.UUID) -> Blog:
    return Blog(
        user_id=sample_user_id,
        title="Lessons from Building a Payment Platform",
        url="https://medium.com/@janedoe/lessons",
        platform="Medium",
        date="2023-08",
        description="Key takeaways from 3 years of building fintech infrastructure.",
    )


@pytest.fixture
def sample_language(sample_user_id: uuid.UUID) -> Language:
    return Language(
        user_id=sample_user_id,
        name="Spanish",
        proficiency="intermediate",
    )
