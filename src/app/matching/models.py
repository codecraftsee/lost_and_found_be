import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MatchStatus(StrEnum):
    PENDING = "pending"
    CLAIM_SUBMITTED = "claim_submitted"
    DISMISSED = "dismissed"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lost_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("items.id"), nullable=False, index=True
    )
    found_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("items.id"), nullable=False, index=True
    )
    status: Mapped[MatchStatus] = mapped_column(String(20), nullable=False, default=MatchStatus.PENDING)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lost_item: Mapped["Item"] = relationship("Item", foreign_keys=[lost_item_id], lazy="selectin")  # noqa: F821
    found_item: Mapped["Item"] = relationship("Item", foreign_keys=[found_item_id], lazy="selectin")  # noqa: F821
