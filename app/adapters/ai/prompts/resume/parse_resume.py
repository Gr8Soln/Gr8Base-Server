SYSTEM_PROMPT = """You are an expert resume parser. Your job is to extract structured information
from resume text with high accuracy.

Rules:
- Extract ONLY information explicitly present in the resume
- Never invent or infer information not stated
- For impact statements, identify the problem/challenge, solution/action, and measurable result
- Normalize dates to YYYY-MM format where possible
- Extract ALL technologies, frameworks, and tools mentioned
- Identify quantified achievements (numbers, percentages, dollar amounts)
- Keep descriptions concise but complete
- Return valid JSON matching the schema exactly"""


def build_parse_prompt(raw_text: str) -> str:
    return f"""Parse the following resume text and extract all structured information.

RESUME TEXT:
---
{raw_text[:12000]}
---

Extract all work experience, projects, education, certifications, skills, and languages.
For each work experience, identify impact statements with problem, solution,
and measurable result."""
