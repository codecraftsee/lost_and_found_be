import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database import get_db
from app.items import service
from app.items.schemas import ItemCreate, ItemDetailResponse, ItemPublicResponse

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=ItemDetailResponse, status_code=201)
async def create_item(
    data: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemDetailResponse:
    item = await service.create_item(db, current_user.id, data)
    return item  # type: ignore[return-value]


@router.get("/mine", response_model=list[ItemDetailResponse])
async def get_my_items(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ItemDetailResponse]:
    items = await service.get_user_items(db, current_user.id)
    return items  # type: ignore[return-value]


@router.get("/{item_id}", response_model=ItemPublicResponse)
async def get_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ItemPublicResponse:
    item = await service.get_item(db, item_id)
    return item  # type: ignore[return-value]
