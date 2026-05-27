import uuid

from app.adapters.renderer.html_renderer import render_resume_html
from app.domain.entities.resume import Education, ImpactStatement, Project, Resume, WorkExperience


def _make_full_resume() -> Resume:
    return Resume(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        file_url="https://r2.example.com/resume.pdf",
        file_name="resume.pdf",
        raw_text="Senior Backend Engineer with Python expertise",
        skills=["Python", "FastAPI", "PostgreSQL", "Redis", "LangGraph", "Docker"],
        experience=[
            WorkExperience(
                id=uuid.uuid4(),
                company="SoluTion Tech Hub",
                role="Senior Backend Engineer",
                start_date="2022-01",
                end_date=None,
                is_current=True,
                location="Lagos, Nigeria",
                description="• Built AI-powered APIs\n• Scaled systems to 10k users",
                technologies=["Python", "FastAPI", "LangGraph"],
                impact_statements=[
                    ImpactStatement(
                        problem="Slow resume parsing",
                        solution="Implemented async LLM pipeline",
                        result="5x throughput increase",
                        metric="5x",
                    )
                ],
            )
        ],
        projects=[
            Project(
                id=uuid.uuid4(),
                name="HireLab",
                description="AI career operating system",
                technologies=["Python", "FastAPI", "LangGraph", "pgvector"],
                url="https://github.com/Gr8Soln/hirelab",
                impact="Automated job applications",
            )
        ],
        education=[
            Education(
                id=uuid.uuid4(),
                institution="Obafemi Awolowo University",
                degree="B.Sc",
                field_of_study="Civil Engineering",
                start_year=2018,
                end_year=2022,
            )
        ],
        languages=["English", "Yoruba"],
        version=2,
        label="ATS Aggressive",
    )


def test_render_classic_template_contains_key_content() -> None:
    resume = _make_full_resume()
    html = render_resume_html(resume, template_name="classic")

    assert "Python" in html
    assert "SoluTion Tech Hub" in html
    assert "HireLab" in html
    assert "Obafemi Awolowo University" in html
    assert "Senior Backend Engineer" in html


def test_render_modern_template_works() -> None:
    resume = _make_full_resume()
    html = render_resume_html(resume, template_name="modern")
    assert "Python" in html
    assert "HireLab" in html


def test_render_minimal_template_works() -> None:
    resume = _make_full_resume()
    html = render_resume_html(resume, template_name="minimal")
    assert "Python" in html
    assert "Obafemi Awolowo University" in html


def test_render_unknown_template_falls_back_to_classic() -> None:
    resume = _make_full_resume()
    html = render_resume_html(resume, template_name="nonexistent_template")
    # Should not raise — falls back gracefully
    assert "Python" in html
    assert "<html" in html


def test_render_empty_resume_does_not_crash() -> None:
    resume = Resume(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        file_url="",
        file_name="empty.pdf",
        raw_text="",
    )
    html = render_resume_html(resume, template_name="classic")
    assert "<html" in html


def test_render_produces_valid_html_structure() -> None:
    resume = _make_full_resume()
    html = render_resume_html(resume, template_name="classic")
    assert "<!DOCTYPE html>" in html
    assert "<body>" in html
    assert "</html>" in html
    assert "<style>" in html


def test_render_skills_all_appear() -> None:
    resume = _make_full_resume()
    html = render_resume_html(resume, template_name="classic")
    for skill in resume.skills:
        assert skill in html
