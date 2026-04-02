import uuid
from datetime import datetime

from pydantic import BaseModel

from app.constants import ItemCategory
from app.items.enums import ItemType, ReportStatus


class ItemCreate(BaseModel):
    item_type: ItemType
    category: ItemCategory
    title: str
    description: str | None = None
    location: str
    date_occurred: datetime
    image_url: str | None = None

    # Private verification fields
    private_brand: str | None = None
    private_color: str | None = None
    private_markings: str | None = None
    private_contents: str | None = None
    private_exact_location: str | None = None


class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    category: ItemCategory | None = None
    image_url: str | None = None
    private_brand: str | None = None
    private_color: str | None = None
    private_markings: str | None = None
    private_contents: str | None = None
    private_exact_location: str | None = None


class ItemPublicResponse(BaseModel):
    id: uuid.UUID
    item_type: ItemType
    status: ReportStatus
    category: ItemCategory
    title: str
    description: str | None
    location: str
    date_occurred: datetime
    image_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ItemDetailResponse(ItemPublicResponse):
    """Full response including private fields — only visible to the item owner."""
    private_brand: str | None
    private_color: str | None
    private_markings: str | None
    private_contents: str | None
    private_exact_location: str | None
    user_id: uuid.UUID
