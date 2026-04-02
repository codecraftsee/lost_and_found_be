import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.claims import service
from app.claims.schemas import ClaimCreate, ClaimResponse, ClaimReview
from app.database import get_db

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.post("/", response_model=ClaimResponse, status_code=201)
async def submit_claim(
    data: ClaimCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClaimResponse:
    claim = await service.submit_claim(db, current_user.id, data)
    return claim  # type: ignore[return-value]


@router.get("/mine", response_model=list[ClaimResponse])
async def get_my_claims(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ClaimResponse]:
    claims = await service.get_user_claims(db, current_user.id)
    return claims  # type: ignore[return-value]


@router.get("/item/{item_id}", response_model=list[ClaimResponse])
async def get_claims_for_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ClaimResponse]:
    claims = await service.get_item_claims(db, item_id)
    return claims  # type: ignore[return-value]


@router.patch("/{claim_id}/review", response_model=ClaimResponse)
async def review_claim(
    claim_id: uuid.UUID,
    data: ClaimReview,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClaimResponse:
    claim = await service.review_claim(db, claim_id, data.approved)
    return claim  # type: ignore[return-value]
