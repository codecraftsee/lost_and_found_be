from enum import StrEnum

# Password rules
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRES_UPPERCASE = True
PASSWORD_REQUIRES_DIGIT = True


class ItemCategory(StrEnum):
    WALLET = "wallet"
    PHONE = "phone"
    KEYS = "keys"
    BAG = "bag"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    JEWELRY = "jewelry"
    DOCUMENTS = "documents"
    OTHER = "other"
