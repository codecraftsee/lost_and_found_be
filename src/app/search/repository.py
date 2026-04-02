from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.items.enums import ReportStatus
from app.items.models import Item
from app.search.schemas import SearchFilters


def apply_filters(query: Select, filters: SearchFilters) -> Select:
    query = query.where(Item.status == ReportStatus.ACTIVE)

    if filters.item_type:
        query = query.where(Item.item_type == filters.item_type)
    if filters.category:
        query = query.where(Item.category == filters.category)
    if filters.location:
        query = query.where(Item.location.ilike(f"%{filters.location}%"))
    if filters.date_from:
        query = query.where(Item.date_occurred >= filters.date_from)
    if filters.date_to:
        query = query.where(Item.date_occurred <= filters.date_to)
    if filters.query:
        search_term = f"%{filters.query}%"
        query = query.where(
            or_(Item.title.ilike(search_term), Item.description.ilike(search_term))
        )

    return query


async def search_items(db: AsyncSession, filters: SearchFilters) -> tuple[list[Item], int]:
    base_query = select(Item)
    filtered_query = apply_filters(base_query, filters)

    # Count total
    count_query = select(func.count()).select_from(filtered_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Paginate
    offset = (filters.page - 1) * filters.page_size
    paginated_query = filtered_query.order_by(Item.created_at.desc()).offset(offset).limit(filters.page_size)
    result = await db.execute(paginated_query)

    return list(result.scalars().all()), total
