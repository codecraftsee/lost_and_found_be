from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import PasswordChange, TokenPair, UserCreate, UserLogin, UserResponse
from app.auth.security import hash_password, verify_password
from app.auth.exceptions import InvalidCredentials
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    return await service.register_user(db, data)


@router.post("/login", response_model=TokenPair)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenPair:
    return await service.authenticate_user(db, data.email, data.password)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.put("/change-password")
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if not verify_password(data.current_password, current_user.hashed_password):
        raise InvalidCredentials()

    current_user.hashed_password = hash_password(data.new_password)
    await db.flush()
    return {"message": "Password changed successfully"}
