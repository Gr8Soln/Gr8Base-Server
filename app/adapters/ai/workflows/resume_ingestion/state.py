from typing import TypedDict


class ResumeIngestionState(TypedDict, total=False):
    # Inputs
    user_id: str
    file_bytes: bytes
    filename: str
    content_type: str

    # Intermediate
    raw_text: str
    storage_key: str
    file_url: str
    resume_id: str
    workflow_id: str

    # Extracted data (populated by parse_career_node)
    extracted_profile: dict
    extracted_experiences: list[dict]
    extracted_projects: list[dict]
    extracted_skills: list[dict]
    extracted_technologies: list[dict]
    extracted_education: list[dict]
    extracted_certifications: list[dict]
    extracted_awards: list[dict]
    extracted_publications: list[dict]
    extracted_blogs: list[dict]
    extracted_languages: list[dict]

    # Enrichment data
    company_enrichments: dict
    technology_enrichments: dict

    # Embeddings
    summary_embedding: list[float]
    experience_embeddings: list[list[float]]
    project_embeddings: list[list[float]]

    # Output
    status: str  # completed / failed
    error_message: str
    errors: list[str]
