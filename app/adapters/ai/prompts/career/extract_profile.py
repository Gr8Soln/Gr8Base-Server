"""Prompt for AI-powered career profile extraction from resume text."""

SYSTEM_PROMPT = """You are an expert career profile extraction system. Your task is to extract
a complete, structured career profile from raw resume or LinkedIn text.

CRITICAL RULES:
1. Extract ALL information faithfully — never fabricate or guess
2. If a field is not present in the source text, leave it empty/default
3. Preserve exact dates, company names, and job titles
4. Extract ALL skills mentioned (both technical and soft)
5. Distinguish between responsibilities (routine tasks) and achievements (notable results)
6. Identify quantified metrics (percentages, dollar amounts, time savings)
7. Group technologies by category where possible
8. Detect languages mentioned (both programming and spoken)
9. Extract ALL projects with their technologies and impact
10. Be thorough — every experience, project, and skill matters
"""


def build_extract_prompt(raw_text: str) -> str:
    return f"""Extract the complete career profile from the following resume text.

Return a structured JSON object with ALL of the following sections.

## Personal Information
- full_name: Full name of the person
- email: Email address
- phone: Phone number
- location: City, State/Country
- linkedin_url: LinkedIn profile URL
- github_url: GitHub profile URL
- portfolio_url: Portfolio/Personal website URL
- headline: Professional headline or current role
- summary: Professional summary paragraph
- years_of_experience: Total years of professional experience (integer)

## Work Experiences (list)
For each position, extract:
- company: Company name
- role: Job title
- start_date: Start date (YYYY-MM format preferred)
- end_date: End date (YYYY-MM, or null if current)
- is_current: Boolean, true if current position
- location: Job location
- description: Brief role description
- employment_type: One of full_time, part_time, contract, freelance, internship, self_employed, volunteer
- responsibilities: List of specific responsibilities
- achievements: List of notable achievements with metrics
- technologies: List of technologies/tools used in this role

## Projects (list)
For each project, extract:
- name: Project name
- description: What the project does
- role: Your role in the project
- technologies: Technologies used
- responsibilities: Your responsibilities
- repository: GitHub/repo URL
- demo_url: Live demo URL
- url: Project URL
- duration: How long you worked on it
- impact: The project's impact or results

## Skills (list)
For each skill, extract:
- name: Skill name (e.g., "Python", "Project Management")
- category: One of technical, soft, language, domain, tool, certification, methodology
- proficiency: beginner, intermediate, advanced, or expert
- years_of_experience: Years using this skill (float, can be decimal)

## Technologies (list)
For each technology/tool, extract:
- name: Technology name (e.g., "Docker", "React", "PostgreSQL")
- category: One of tool, technical, language, domain, methodology
- proficiency: beginner, intermediate, advanced, or expert

## Education (list)
For each entry, extract:
- institution: School/university name
- degree: Degree earned (e.g., "B.S. Computer Science")
- field_of_study: Major/concentration
- start_year: Start year (integer)
- end_year: End year (integer)
- gpa: GPA if available (float)
- honors: Honors or distinctions
- activities: Notable activities

## Certifications (list)
For each, extract:
- name: Certification name
- issuer: Issuing organization
- issue_date: Date issued
- expiry_date: Expiration date
- credential_url: Verification URL
- credential_id: Credential ID number

## Awards (list)
For each, extract:
- name: Award name
- issuer: Who gave the award
- date: When awarded
- description: What it was for

## Publications (list)
For each, extract:
- title: Publication title
- publisher: Publisher/journal name
- date: Publication date
- url: Link to publication
- description: Brief description

## Blogs (list)
For each, extract:
- title: Blog post title
- url: Link to blog post
- platform: Platform (Medium, Dev.to, personal, etc.)
- date: Publication date
- description: Brief description

## Languages (list)
For each, extract:
- name: Language name
- proficiency: native, fluent, intermediate, or basic

--- RESUME TEXT ---
{raw_text[:15000]}
--- END ---

Extract the complete career profile now. Be thorough and accurate."""
