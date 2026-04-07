import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.utils.validators import validate_password_strength


class UserCreate(BaseModel):
    email: EmailStr = Field(description="Valid email address. Used as the unique login identifier.", examples=["jane.doe@example.com"])
    password: str = Field(description="Min 8 characters, at least 1 uppercase letter and 1 digit.", examples=["Secret123"])
    full_name: str = Field(description="Display name shown on the user profile.", examples=["Jane Doe"])

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserLogin(BaseModel):
    email: EmailStr = Field(examples=["jane.doe@example.com"])
    password: str = Field(examples=["Secret123"])


class UserResponse(BaseModel):
    id: uuid.UUID = Field(description="Unique user identifier.")
    email: EmailStr
    full_name: str
    is_active: bool = Field(description="False if the account has been deactivated.")
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    access_token: str = Field(description="Short-lived JWT for authenticating API requests. Valid for 30 minutes.")
    refresh_token: str = Field(description="Long-lived JWT for obtaining new token pairs. Valid for 7 days.")
    token_type: str = Field(default="bearer", description="Always 'bearer'. Include as 'Authorization: Bearer <access_token>'.")


class TokenRefresh(BaseModel):
    refresh_token: str = Field(description="A valid refresh token previously issued by POST /auth/login or POST /auth/refresh.")


class PasswordChange(BaseModel):
    current_password: str = Field(description="The user's existing password for verification.")
    new_password: str = Field(description="Min 8 characters, at least 1 uppercase letter and 1 digit.")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)


class PasswordReset(BaseModel):
    email: EmailStr
