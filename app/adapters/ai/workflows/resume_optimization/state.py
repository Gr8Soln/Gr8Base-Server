from typing import TypedDict


class ResumeOptimizationState(TypedDict):
    # Inputs
    user_id: str
    resume_id: str
    job_id: str
    strategy_mode: str

    # Raw data
    original_resume: dict
    job_data: dict

    # Strategy planning
    optimization_directives: dict
    section_order: list[str]
    tone: str
    emphasis_keywords: list[str]
    deemphasize: list[str]

    # Bullet optimization — per experience entry
    optimized_experience: list[dict]

    # Keyword injection
    injected_skills: list[str]
    final_skills: list[str]

    # Assembled optimized resume
    optimized_resume: dict

    # Evaluation loop
    pre_ats_score: float
    post_ats_score: float
    evaluation_passed: bool
    iteration: int
    max_iterations: int

    # Critic pass
    critique_passed: bool
    critique_feedback: str
    weak_points: list[str]

    # Rendering
    html_content: str
    pdf_url: str

    # Control
    errors: list[str]
