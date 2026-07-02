SYSTEM_PROMPT = """You are an expert resume writer specializing in ATS optimization and
recruiter readability.

Rewrite resume bullet points to:
1. Lead with strong action verbs
2. Include quantified metrics where possible
3. Naturally incorporate ATS keywords without stuffing
4. Follow STAR format (Action, Result)
5. Be concise — 1-2 lines max per bullet
6. Sound human — never generic AI language

CRITICAL: Only rewrite — never fabricate metrics or experiences not in the original.
Return valid JSON only."""


def build_bullet_prompt(
    experience: dict,
    target_keywords: list[str],
    job_role: str,
    tone: str,
) -> str:
    impacts = experience.get("impact_statements", [])
    description = experience.get("description", "")

    impact_lines = "\n".join(
        f"- Problem: {i.get('problem')} | Solution: {i.get('solution')} "
        f"| Result: {i.get('result')} | Metric: {i.get('metric')}"
        for i in impacts
    )

    keywords_str = ", ".join(target_keywords[:10])

    return f"""Rewrite bullets for this work experience entry.

ROLE: {experience.get('role')} at {experience.get('company')}
TARGET JOB ROLE: {job_role}
TONE: {tone}
ATS KEYWORDS TO INCORPORATE: {keywords_str}

CURRENT CONTENT:
Description: {description}
Impact statements:
{impact_lines}

Rewrite as 3-5 strong ATS-optimized bullet points using metrics from the original only."""
