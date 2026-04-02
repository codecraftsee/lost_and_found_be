from app.exceptions import AppException


class ItemNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(status_code=404, detail="Item not found")


class NotItemOwner(AppException):
    def __init__(self) -> None:
        super().__init__(status_code=403, detail="You are not the owner of this item")
