import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.items.enums import ItemType, ReportStatus
from app.items.models import Item


async def create_item(db: AsyncSession, item: Item) -> Item:
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def get_item_by_id(db: AsyncSession, item_id: uuid.UUID) -> Item | None:
    result = await db.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()


async def get_items_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[Item]:
    result = await db.execute(
        select(Item).where(Item.user_id == user_id).order_by(Item.created_at.desc())
    )
    return list(result.scalars().all())


async def get_active_items_by_type(db: AsyncSession, item_type: ItemType) -> list[Item]:
    result = await db.execute(
        select(Item)
        .where(Item.item_type == item_type, Item.status == ReportStatus.ACTIVE)
        .order_by(Item.created_at.desc())
    )
    return list(result.scalars().all())
