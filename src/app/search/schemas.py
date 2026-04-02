from datetime import datetime

from pydantic import BaseModel

from app.constants import ItemCategory
from app.items.enums import ItemType
from app.items.schemas import ItemPublicResponse


class SearchFilters(BaseModel):
    query: str | None = None
    category: ItemCategory | None = None
    item_type: ItemType | None = None
    location: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel):
    items: list[ItemPublicResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
