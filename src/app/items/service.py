import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.items import repository
from app.items.exceptions import ItemNotFound, NotItemOwner
from app.items.models import Item
from app.items.schemas import ItemCreate


async def create_item(db: AsyncSession, user_id: uuid.UUID, data: ItemCreate) -> Item:
    item = Item(
        user_id=user_id,
        item_type=data.item_type,
        category=data.category,
        title=data.title,
        description=data.description,
        location=data.location,
        date_occurred=data.date_occurred,
        image_url=data.image_url,
        private_brand=data.private_brand,
        private_color=data.private_color,
        private_markings=data.private_markings,
        private_contents=data.private_contents,
        private_exact_location=data.private_exact_location,
    )
    item = await repository.create_item(db, item)

    # TODO: Trigger automatic matching after item creation
    # await matching_service.find_matches(db, item)

    return item


async def get_item(db: AsyncSession, item_id: uuid.UUID) -> Item:
    item = await repository.get_item_by_id(db, item_id)
    if not item:
        raise ItemNotFound()
    return item


async def get_user_items(db: AsyncSession, user_id: uuid.UUID) -> list[Item]:
    return await repository.get_items_by_user(db, user_id)


async def verify_item_ownership(item: Item, user_id: uuid.UUID) -> None:
    if item.user_id != user_id:
        raise NotItemOwner()
