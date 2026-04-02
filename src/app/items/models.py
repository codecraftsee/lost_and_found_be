import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import ItemCategory
from app.database import Base
from app.items.enums import ItemType, ReportStatus


class Item(Base):
    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    item_type: Mapped[ItemType] = mapped_column(String(10), nullable=False, index=True)
    status: Mapped[ReportStatus] = mapped_column(String(20), nullable=False, default=ReportStatus.ACTIVE, index=True)

    # Public fields
    category: Mapped[ItemCategory] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    date_occurred: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Private verification fields (hidden from public view)
    private_brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    private_color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    private_markings: Mapped[str | None] = mapped_column(Text, nullable=True)
    private_contents: Mapped[str | None] = mapped_column(Text, nullable=True)
    private_exact_location: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", lazy="selectin")  # noqa: F821
