SYSTEM_PROMPT = """You are an expert resume strategist. Your job is to determine the optimal
optimization strategy for a resume targeting a specific job description.

You analyze the gap between the current resume and the target role, then produce
a precise set of directives that will guide the optimization agents.

Return valid JSON only."""


def build_strategy_prompt(resume_data: dict, job_data: dict, strategy_mode: str) -> str:
    return f"""Analyze this resume against the job description and produce optimization directives.

OPTIMIZATION MODE: {strategy_mode}

CURRENT RESUME SUMMARY:
Skills: {', '.join(resume_data.get('skills', [])[:20])}
Experience roles: {[e.get('role') for e in resume_data.get('experience', [])]}
Projects: {[p.get('name') for p in resume_data.get('projects', [])]}

TARGET JOB:
Role: {job_data.get('role')} ({job_data.get('seniority')})
Domain: {job_data.get('domain')}
Required: {', '.join(job_data.get('required_skills', []))}
ATS Keywords: {', '.join(job_data.get('ats_keywords', [])[:15])}
Hidden signals: {job_data.get('hidden_signals', [])}

Produce specific directives for: section ordering, keyword injection priorities,
tone adjustments, content emphasis, and what to de-emphasize."""
