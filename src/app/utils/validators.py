import re

from app.constants import PASSWORD_MIN_LENGTH, PASSWORD_REQUIRES_DIGIT, PASSWORD_REQUIRES_UPPERCASE


def validate_password_strength(v: str) -> str:
    if len(v) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
    if PASSWORD_REQUIRES_UPPERCASE and not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain at least one uppercase letter")
    if PASSWORD_REQUIRES_DIGIT and not re.search(r"\d", v):
        raise ValueError("Password must contain at least one digit")
    return v
