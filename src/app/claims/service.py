import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.claims import repository
from app.claims.exceptions import CannotClaimOwnItem, ClaimNotFound, CooldownActive, TooManyAttempts
from app.claims.models import Claim, ClaimStatus
from app.claims.schemas import ClaimCreate
from app.claims.verification import verify_claim_answers
from app.config import settings
from app.items import service as items_service


async def submit_claim(db: AsyncSession, user_id: uuid.UUID, data: ClaimCreate) -> Claim:
    item = await items_service.get_item(db, data.item_id)

    # Cannot claim your own item
    if item.user_id == user_id:
        raise CannotClaimOwnItem()

    # Check for existing claim by this user on this item
    existing = await repository.get_claim_by_user_and_item(db, user_id, data.item_id)
    if existing:
        # Check cooldown
        if existing.cooldown_until and existing.cooldown_until > datetime.now(timezone.utc):
            raise CooldownActive()

        # Check max attempts
        if existing.attempts >= settings.CLAIM_MAX_ATTEMPTS:
            raise TooManyAttempts()

        # Update existing claim with new answers
        existing.answer_brand = data.answer_brand
        existing.answer_color = data.answer_color
        existing.answer_markings = data.answer_markings
        existing.answer_contents = data.answer_contents
        existing.answer_exact_location = data.answer_exact_location
        existing.attempts += 1

        is_verified, _ = verify_claim_answers(existing, item)
        if is_verified:
            existing.status = ClaimStatus.VERIFIED
        else:
            # Set cooldown after failed attempt
            existing.cooldown_until = datetime.now(timezone.utc) + timedelta(minutes=settings.CLAIM_COOLDOWN_MINUTES)
            existing.status = ClaimStatus.PENDING

        await db.flush()
        await db.refresh(existing)
        return existing

    # Create new claim
    claim = Claim(
        claimant_id=user_id,
        item_id=data.item_id,
        answer_brand=data.answer_brand,
        answer_color=data.answer_color,
        answer_markings=data.answer_markings,
        answer_contents=data.answer_contents,
        answer_exact_location=data.answer_exact_location,
        attempts=1,
    )

    is_verified, _ = verify_claim_answers(claim, item)
    if is_verified:
        claim.status = ClaimStatus.VERIFIED
    else:
        claim.cooldown_until = datetime.now(timezone.utc) + timedelta(minutes=settings.CLAIM_COOLDOWN_MINUTES)

    return await repository.create_claim(db, claim)


async def get_user_claims(db: AsyncSession, user_id: uuid.UUID) -> list[Claim]:
    return await repository.get_claims_by_user(db, user_id)


async def get_item_claims(db: AsyncSession, item_id: uuid.UUID) -> list[Claim]:
    return await repository.get_claims_for_item(db, item_id)


async def review_claim(db: AsyncSession, claim_id: uuid.UUID, approved: bool) -> Claim:
    claim = await repository.get_claim_by_id(db, claim_id)
    if not claim:
        raise ClaimNotFound()

    claim.status = ClaimStatus.APPROVED if approved else ClaimStatus.REJECTED
    await db.flush()
    await db.refresh(claim)
    return claim
