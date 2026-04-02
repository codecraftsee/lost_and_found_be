import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import repository
from app.auth.exceptions import InvalidCredentials
from app.auth.models import User
from app.auth.security import decode_token
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise InvalidCredentials()

    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidCredentials()

    user = await repository.get_user_by_id(db, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise InvalidCredentials()

    return user
