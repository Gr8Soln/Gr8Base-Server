SYSTEM_PROMPT = """You are a senior technical recruiter and hiring manager with 10+ years
of experience. You have reviewed thousands of resumes.

Do a final quality pass and identify:
1. Whether it passes a 6-second recruiter scan
2. Any remaining weaknesses
3. ATS compatibility issues
4. Tone or language problems
5. Whether the overall narrative is compelling

Be direct and specific. Reference actual content. Return valid JSON only."""


def build_critic_prompt(optimized_resume: dict, job_data: dict) -> str:
    experience_lines = "\n".join(
        f"- {e.get('role')} at {e.get('company')}: "
        f"{e.get('optimized_bullets', [])[:2]}"
        for e in optimized_resume.get("experience", [])[:3]
    )
    skills_preview = ", ".join(optimized_resume.get("skills", [])[:25])

    return f"""Review this optimized resume for the target role.

TARGET: {job_data.get('title')} at {job_data.get('company', 'target company')}
SENIORITY: {job_data.get('seniority')}
DOMAIN: {job_data.get('domain')}

OPTIMIZED RESUME SUMMARY:
Skills ({len(optimized_resume.get('skills', []))} total): {skills_preview}

Experience:
{experience_lines}

Does this pass the 6-second scan? What would make a recruiter stop reading?
What still needs improvement?"""
