from enum import StrEnum


class ResumeStrategy(StrEnum):
    ATS_AGGRESSIVE = "ats_aggressive"
    RECRUITER_FRIENDLY = "recruiter_friendly"
    STARTUP_LEAN = "startup_lean"
    ENTERPRISE_FORMAL = "enterprise_formal"
    TECHNICAL_DEEP_DIVE = "technical_deep_dive"
    EXECUTIVE_STYLE = "executive_style"
    ONE_PAGE_COMPRESSION = "one_page_compression"
    FAANG_STYLE = "faang_style"
    EUROPEAN_CV = "european_cv"
