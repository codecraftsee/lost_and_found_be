from enum import StrEnum


class ItemType(StrEnum):
    LOST = "lost"
    FOUND = "found"


class ReportStatus(StrEnum):
    ACTIVE = "active"
    CLAIMED = "claimed"
    RESOLVED = "resolved"
    EXPIRED = "expired"
    CLOSED = "closed"
