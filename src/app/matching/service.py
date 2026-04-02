import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.items.enums import ItemType, ReportStatus
from app.items.models import Item
from app.items.repository import get_active_items_by_type
from app.matching import repository
from app.matching.exceptions import MatchNotFound
from app.matching.models import Match


def _calculate_match_score(item_a: Item, item_b: Item) -> float:
    """Calculate a simple match score between a lost and found item."""
    score = 0.0

    # Category match (required — if no match, score stays 0)
    if item_a.category != item_b.category:
        return 0.0
    score += 40.0

    # Location similarity (simple substring check for MVP)
    if item_a.location and item_b.location:
        if item_a.location.lower() == item_b.location.lower():
            score += 30.0
        elif item_a.location.lower() in item_b.location.lower() or item_b.location.lower() in item_a.location.lower():
            score += 15.0

    # Date proximity (found date should be on or after lost date)
    if item_a.date_occurred and item_b.date_occurred:
        days_diff = abs((item_a.date_occurred - item_b.date_occurred).days)
        if days_diff <= 1:
            score += 20.0
        elif days_diff <= 7:
            score += 10.0
        elif days_diff <= 30:
            score += 5.0

    # Keyword overlap in title/description
    words_a = set((item_a.title + " " + (item_a.description or "")).lower().split())
    words_b = set((item_b.title + " " + (item_b.description or "")).lower().split())
    common_words = words_a & words_b - {"a", "the", "an", "in", "on", "at", "is", "was", "my", "i"}
    if len(common_words) >= 3:
        score += 10.0
    elif len(common_words) >= 1:
        score += 5.0

    return score


async def find_matches_for_item(db: AsyncSession, item: Item, min_score: float = 30.0) -> list[Match]:
    """Find potential matches for a newly created item."""
    opposite_type = ItemType.FOUND if item.item_type == ItemType.LOST else ItemType.LOST
    candidates = await get_active_items_by_type(db, opposite_type)

    matches = []
    for candidate in candidates:
        lost_item = item if item.item_type == ItemType.LOST else candidate
        found_item = candidate if item.item_type == ItemType.LOST else item

        score = _calculate_match_score(lost_item, found_item)
        if score >= min_score:
            match = Match(
                lost_item_id=lost_item.id,
                found_item_id=found_item.id,
                score=score,
            )
            match = await repository.create_match(db, match)
            matches.append(match)

    return matches


async def get_user_matches(db: AsyncSession, item_ids: list[uuid.UUID]) -> list[Match]:
    return await repository.get_matches_for_user_items(db, item_ids)


async def dismiss_match(db: AsyncSession, match_id: uuid.UUID) -> Match:
    match = await repository.get_match_by_id(db, match_id)
    if not match:
        raise MatchNotFound()
    return await repository.dismiss_match(db, match)
