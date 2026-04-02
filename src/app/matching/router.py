import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database import get_db
from app.items import repository as items_repo
from app.matching import service
from app.matching.schemas import MatchResponse

router = APIRouter(prefix="/matches", tags=["Matching"])


@router.get("/", response_model=list[MatchResponse])
async def get_my_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MatchResponse]:
    user_items = await items_repo.get_items_by_user(db, current_user.id)
    item_ids = [item.id for item in user_items]
    matches = await service.get_user_matches(db, item_ids)
    return matches  # type: ignore[return-value]


@router.patch("/{match_id}/dismiss", response_model=MatchResponse)
async def dismiss_match(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MatchResponse:
    match = await service.dismiss_match(db, match_id)
    return match  # type: ignore[return-value]
