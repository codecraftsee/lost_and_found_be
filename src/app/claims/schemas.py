import uuid
from datetime import datetime

from pydantic import BaseModel

from app.claims.models import ClaimStatus


class ClaimCreate(BaseModel):
    item_id: uuid.UUID
    answer_brand: str | None = None
    answer_color: str | None = None
    answer_markings: str | None = None
    answer_contents: str | None = None
    answer_exact_location: str | None = None


class ClaimResponse(BaseModel):
    id: uuid.UUID
    claimant_id: uuid.UUID
    item_id: uuid.UUID
    status: ClaimStatus
    attempts: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ClaimReview(BaseModel):
    approved: bool
