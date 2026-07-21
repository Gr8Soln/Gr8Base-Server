import uuid

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
from app.domain.enums.ingestion_status import IngestionStatus
from app.domain.enums.skill_category import SkillCategory


class TestCareerProfile:
    def test_create_career_profile(self, sample_user_id):
        profile = CareerProfile(
            user_id=sample_user_id,
            full_name="Jane Doe",
            email="jane@example.com",
        )
        assert profile.user_id == sample_user_id
        assert profile.full_name == "Jane Doe"
        assert profile.email == "jane@example.com"
        assert profile.headline == ""
        assert profile.summary == ""
        assert profile.years_of_experience == 0
        assert isinstance(profile.id, uuid.UUID)

    def test_career_profile_defaults(self, sample_user_id):
        profile = CareerProfile(user_id=sample_user_id, full_name="Test", email="test@test.com")
        assert profile.target_roles == []
        assert profile.target_industries == []
        assert profile.writing_tone == "professional"

    def test_career_profile_with_all_fields(self, sample_career_profile):
        assert sample_career_profile.headline == "Senior Software Engineer"
        assert sample_career_profile.years_of_experience == 10
        assert "Staff Engineer" in sample_career_profile.target_roles


class TestWorkExperience:
    def test_create_experience(self, sample_user_id):
        exp = WorkExperience(
            user_id=sample_user_id,
            company="Acme Corp",
            role="Engineer",
            start_date="2020-01",
        )
        assert exp.company == "Acme Corp"
        assert exp.role == "Engineer"
        assert exp.employment_type == EmploymentType.FULL_TIME
        assert isinstance(exp.id, uuid.UUID)

    def test_experience_with_impacts(self, sample_experience):
        assert len(sample_experience.impact_statements) == 1
        assert sample_experience.impact_statements[0].metric == "40%"
        assert sample_experience.is_current is True

    def test_experience_technologies(self, sample_experience):
        assert "Python" in sample_experience.technologies
        assert "Kubernetes" in sample_experience.technologies


class TestImpactStatement:
    def test_create_impact(self):
        impact = ImpactStatement(
            problem="Slow queries",
            solution="Added caching",
            result="10x faster",
            metric="10x",
        )
        assert impact.problem == "Slow queries"
        assert impact.metric == "10x"


class TestProject:
    def test_create_project(self, sample_user_id):
        proj = Project(
            user_id=sample_user_id,
            name="Test Project",
            description="A test project",
        )
        assert proj.name == "Test Project"
        assert proj.technologies == []

    def test_project_full(self, sample_project):
        assert sample_project.role == "Lead Architect"
        assert "Redis" in sample_project.technologies


class TestSkill:
    def test_create_skill(self, sample_user_id):
        skill = Skill(user_id=sample_user_id, name="Python")
        assert skill.name == "Python"
        assert skill.category == SkillCategory.TECHNICAL
        assert skill.years_of_experience == 0.0

    def test_skill_with_proficiency(self, sample_skill):
        assert sample_skill.proficiency == "expert"
        assert sample_skill.years_of_experience == 8.0


class TestTechnology:
    def test_create_technology(self, sample_user_id):
        tech = Technology(user_id=sample_user_id, name="Docker")
        assert tech.name == "Docker"
        assert tech.category == SkillCategory.TOOL


class TestEducation:
    def test_create_education(self, sample_user_id):
        edu = Education(
            user_id=sample_user_id,
            institution="MIT",
            degree="B.S.",
        )
        assert edu.institution == "MIT"
        assert edu.start_year is None

    def test_education_full(self, sample_education):
        assert sample_education.gpa == 3.8
        assert sample_education.honors == "Magna Cum Laude"


class TestCertification:
    def test_create_certification(self, sample_user_id):
        cert = Certification(
            user_id=sample_user_id,
            name="AWS Certified",
            issuer="Amazon",
        )
        assert cert.name == "AWS Certified"

    def test_certification_full(self, sample_certification):
        assert sample_certification.credential_id == "ABC123"


class TestAward:
    def test_create_award(self, sample_user_id):
        award = Award(user_id=sample_user_id, name="Best Engineer", issuer="Company")
        assert award.name == "Best Engineer"

    def test_award_full(self, sample_award):
        assert sample_award.description != ""


class TestPublication:
    def test_create_publication(self, sample_user_id):
        pub = Publication(
            user_id=sample_user_id, title="My Paper", publisher="Journal"
        )
        assert pub.title == "My Paper"
        assert pub.publisher == "Journal"


class TestBlog:
    def test_create_blog(self, sample_user_id):
        blog = Blog(user_id=sample_user_id, title="My Post", url="https://example.com")
        assert blog.title == "My Post"
        assert blog.url == "https://example.com"


class TestLanguage:
    def test_create_language(self, sample_user_id):
        lang = Language(user_id=sample_user_id, name="French")
        assert lang.name == "French"
        assert lang.proficiency == ""


class TestEnums:
    def test_employment_type_values(self):
        assert EmploymentType.FULL_TIME == "full_time"
        assert EmploymentType.CONTRACT == "contract"

    def test_skill_category_values(self):
        assert SkillCategory.TECHNICAL == "technical"
        assert SkillCategory.SOFT == "soft"

    def test_ingestion_status_values(self):
        assert IngestionStatus.PENDING == "pending"
        assert IngestionStatus.COMPLETED == "completed"
        assert IngestionStatus.FAILED == "failed"
