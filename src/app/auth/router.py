from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import PasswordChange, TokenPair, TokenRefresh, UserCreate, UserLogin, UserResponse
from app.auth.security import hash_password, verify_password
from app.auth.exceptions import InvalidCredentials
from app.database import get_db
from app.middleware.rate_limit import RateLimiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

auth_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user",
    responses={
        409: {"description": "Email already registered"},
        422: {"description": "Validation error (invalid email or weak password)"},
        429: {"description": "Too many requests (5 per minute per IP)"},
    },
    dependencies=[Depends(auth_rate_limiter.check)],
)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """
    Create a new user account.

    Password requirements: minimum 8 characters, at least one uppercase letter, at least one digit.
    """
    return await service.register_user(db, data)


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Authenticate and obtain tokens",
    responses={
        401: {"description": "Invalid email or password"},
        429: {"description": "Too many requests (5 per minute per IP)"},
    },
    dependencies=[Depends(auth_rate_limiter.check)],
)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenPair:
    """
    Authenticate with email and password. Returns an access token (30 min) and a refresh token (7 days).

    Use the access token as `Authorization: Bearer <access_token>` on protected endpoints.
    """
    return await service.authenticate_user(db, data.email, data.password)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Rotate tokens using a refresh token",
    responses={
        401: {"description": "Refresh token is invalid, expired, or has wrong type"},
    },
)
async def refresh(data: TokenRefresh, db: AsyncSession = Depends(get_db)) -> TokenPair:
    """
    Exchange a valid refresh token for a new access token and refresh token.

    Both tokens are rotated on every call. The previous refresh token is no longer usable after rotation.
    """
    return await service.refresh_tokens(db, data.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the authenticated user's profile",
    responses={
        401: {"description": "Missing or invalid access token"},
    },
)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the profile of the currently authenticated user."""
    return current_user


@router.put(
    "/change-password",
    summary="Change password for the authenticated user",
    responses={
        401: {"description": "Missing, invalid access token, or wrong current password"},
        422: {"description": "New password does not meet strength requirements"},
    },
)
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Change the authenticated user's password.

    Requires the current password for verification. The new password must meet strength requirements
    (min 8 characters, at least one uppercase letter, at least one digit).
    """
    if not verify_password(data.current_password, current_user.hashed_password):
        raise InvalidCredentials()

    current_user.hashed_password = hash_password(data.new_password)
    await db.flush()
    return {"message": "Password changed successfully"}
