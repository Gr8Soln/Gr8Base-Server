from enum import StrEnum


class OutreachType(StrEnum):
    RECRUITER_EMAIL = "recruiter_email"
    HIRING_MANAGER_INTRO = "hiring_manager_intro"
    REFERRAL_REQUEST = "referral_request"
    FOLLOW_UP = "follow_up"
    THANK_YOU_NOTE = "thank_you_note"
    CONNECTION_REQUEST = "connection_request"
