import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.matching.models import Match, MatchStatus


async def create_match(db: AsyncSession, match: Match) -> Match:
    db.add(match)
    await db.flush()
    await db.refresh(match)
    return match


async def get_matches_for_user_items(db: AsyncSession, item_ids: list[uuid.UUID]) -> list[Match]:
    if not item_ids:
        return []
    result = await db.execute(
        select(Match)
        .where(
            (Match.lost_item_id.in_(item_ids)) | (Match.found_item_id.in_(item_ids))
        )
        .order_by(Match.score.desc())
    )
    return list(result.scalars().all())


async def get_match_by_id(db: AsyncSession, match_id: uuid.UUID) -> Match | None:
    result = await db.execute(select(Match).where(Match.id == match_id))
    return result.scalar_one_or_none()


async def dismiss_match(db: AsyncSession, match: Match) -> Match:
    match.status = MatchStatus.DISMISSED
    await db.flush()
    await db.refresh(match)
    return match
