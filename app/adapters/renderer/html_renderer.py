from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.domain.entities.resume import Resume
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates" / "resume"

_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_resume_html(resume: Resume, template_name: str = "classic") -> str:
    """Renders a Resume entity to HTML string using the specified template."""
    try:
        template = _jinja_env.get_template(f"{template_name}.html")
    except Exception:
        logger.warning("template_not_found", template=template_name, fallback="classic")
        template = _jinja_env.get_template("classic.html")

    context = {
        "resume": resume,
        "skills_chunked": _chunk_list(resume.skills, 4),
    }
    html = template.render(**context)
    logger.info("html_rendered", resume_id=str(resume.id), template=template_name)
    return html


def _chunk_list(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]
