from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ItemCategory
from app.database import get_db
from app.items.enums import ItemType
from app.search import service
from app.search.schemas import PaginatedResponse, SearchFilters

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/", response_model=PaginatedResponse)
async def search_items(
    query: str | None = Query(None),
    category: ItemCategory | None = Query(None),
    item_type: ItemType | None = Query(None),
    location: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    filters = SearchFilters(
        query=query,
        category=category,
        item_type=item_type,
        location=location,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return await service.search_items(db, filters)
