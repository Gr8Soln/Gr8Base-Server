import uuid

from app.adapters.persistence.mappers.user_mapper import CareerProfileMapper, UserMapper
from app.adapters.persistence.models.career_profile_model import CareerProfileModel
from app.adapters.persistence.models.user_model import UserModel
from app.domain.entities.user import User
from app.infrastructure.security.password_handler import hash_password


def test_user_model_to_entity_roundtrip() -> None:
    model = UserModel(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=hash_password("secret"),
        full_name="Test User",
        is_active=True,
        is_verified=False,
        is_superuser=False,
    )

    entity = UserMapper.to_entity(model)

    assert entity.id == model.id
    assert entity.email == model.email
    assert entity.full_name == model.full_name
    assert entity.is_active is True
    assert entity.is_verified is False


def test_user_entity_to_model_roundtrip() -> None:
    entity = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=hash_password("secret"),
        full_name="Test User",
    )

    model = UserMapper.to_model(entity)

    assert model.id == entity.id
    assert model.email == entity.email
    assert model.full_name == entity.full_name


def test_career_profile_mapper_roundtrip() -> None:
    user_id = uuid.uuid4()
    model = CareerProfileModel(
        id=uuid.uuid4(),
        user_id=user_id,
        full_name="Emmanuel",
        email="e@gr8soln.dev",
        headline="Senior Backend Engineer",
        summary="Building AI systems",
        location="Lagos, Nigeria",
        phone="+234...",
        linkedin_url="https://linkedin.com/in/gr8soln",
        github_url="https://github.com/Gr8Soln",
        portfolio_url="https://gr8soln.vercel.app",
        years_of_experience=5,
        target_roles=["Backend Engineer", "AI Engineer"],
        target_industries=["Fintech", "SaaS"],
        target_salary_min=50000,
        target_salary_max=90000,
        preferred_work_type="remote",
        writing_tone="professional",
    )

    entity = CareerProfileMapper.to_entity(model)

    assert entity.user_id == user_id
    assert entity.full_name == "Emmanuel"
    assert entity.years_of_experience == 5
    assert "Backend Engineer" in entity.target_roles
    assert entity.target_salary_min == 50000
