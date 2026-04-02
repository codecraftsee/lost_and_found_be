import math

from sqlalchemy.ext.asyncio import AsyncSession

from app.search import repository
from app.search.schemas import PaginatedResponse, SearchFilters


async def search_items(db: AsyncSession, filters: SearchFilters) -> PaginatedResponse:
    items, total = await repository.search_items(db, filters)
    total_pages = math.ceil(total / filters.page_size) if filters.page_size > 0 else 0

    return PaginatedResponse(
        items=items,  # type: ignore[arg-type]
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=total_pages,
    )
