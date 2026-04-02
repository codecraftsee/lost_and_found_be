import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.claims.models import Claim


async def create_claim(db: AsyncSession, claim: Claim) -> Claim:
    db.add(claim)
    await db.flush()
    await db.refresh(claim)
    return claim


async def get_claim_by_id(db: AsyncSession, claim_id: uuid.UUID) -> Claim | None:
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    return result.scalar_one_or_none()


async def get_claims_for_item(db: AsyncSession, item_id: uuid.UUID) -> list[Claim]:
    result = await db.execute(
        select(Claim).where(Claim.item_id == item_id).order_by(Claim.created_at.desc())
    )
    return list(result.scalars().all())


async def get_claim_by_user_and_item(db: AsyncSession, user_id: uuid.UUID, item_id: uuid.UUID) -> Claim | None:
    result = await db.execute(
        select(Claim).where(Claim.claimant_id == user_id, Claim.item_id == item_id)
    )
    return result.scalar_one_or_none()


async def get_claims_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[Claim]:
    result = await db.execute(
        select(Claim).where(Claim.claimant_id == user_id).order_by(Claim.created_at.desc())
    )
    return list(result.scalars().all())
