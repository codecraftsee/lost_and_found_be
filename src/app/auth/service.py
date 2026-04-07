from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import repository
import uuid

from app.auth.exceptions import InvalidCredentials, InvalidToken, UserAlreadyExists
from app.auth.models import User
from app.auth.schemas import TokenPair, UserCreate
from app.auth.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password


async def register_user(db: AsyncSession, data: UserCreate) -> User:
    existing = await repository.get_user_by_email(db, data.email)
    if existing:
        raise UserAlreadyExists()

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    return await repository.create_user(db, user)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> TokenPair:
    user = await repository.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentials()

    token_data = {"sub": str(user.id)}
    return TokenPair(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenPair:
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise InvalidToken()

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise InvalidToken()

    user = await repository.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise InvalidToken()

    token_data = {"sub": str(user.id)}
    return TokenPair(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )
