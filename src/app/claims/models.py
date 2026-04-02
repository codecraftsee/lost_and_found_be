import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ClaimStatus(StrEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    APPROVED = "approved"


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claimant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("items.id"), nullable=False, index=True
    )
    status: Mapped[ClaimStatus] = mapped_column(String(20), nullable=False, default=ClaimStatus.PENDING)

    # Verification answers
    answer_brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    answer_color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    answer_markings: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_contents: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_exact_location: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Fraud prevention
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cooldown_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    claimant: Mapped["User"] = relationship("User", lazy="selectin")  # noqa: F821
    item: Mapped["Item"] = relationship("Item", lazy="selectin")  # noqa: F821
