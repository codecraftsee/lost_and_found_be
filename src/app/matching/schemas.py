import uuid
from datetime import datetime

from pydantic import BaseModel

from app.items.schemas import ItemPublicResponse
from app.matching.models import MatchStatus


class MatchResponse(BaseModel):
    id: uuid.UUID
    lost_item: ItemPublicResponse
    found_item: ItemPublicResponse
    status: MatchStatus
    score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class MatchDismiss(BaseModel):
    match_id: uuid.UUID
