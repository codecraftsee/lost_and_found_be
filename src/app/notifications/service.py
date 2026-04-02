import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications import repository
from app.notifications.models import Notification, NotificationType


async def create_notification(
    db: AsyncSession,
    user_id: uuid.UUID,
    notification_type: NotificationType,
    title: str,
    message: str,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
    )
    return await repository.create_notification(db, notification)


async def get_user_notifications(db: AsyncSession, user_id: uuid.UUID) -> list[Notification]:
    return await repository.get_user_notifications(db, user_id)


async def mark_notification_read(db: AsyncSession, notification_id: uuid.UUID, user_id: uuid.UUID) -> None:
    await repository.mark_as_read(db, notification_id, user_id)
