from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)

class ConfirmEmailRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)

class ResendConfirmEmailRequest(BaseModel):
    email: EmailStr


