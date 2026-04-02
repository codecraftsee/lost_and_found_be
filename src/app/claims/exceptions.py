from app.exceptions import AppException


class TooManyAttempts(AppException):
    def __init__(self) -> None:
        super().__init__(status_code=429, detail="Too many claim attempts. Please try again later.")


class CooldownActive(AppException):
    def __init__(self) -> None:
        super().__init__(status_code=429, detail="Claim cooldown is active. Please try again later.")


class ClaimNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(status_code=404, detail="Claim not found")


class CannotClaimOwnItem(AppException):
    def __init__(self) -> None:
        super().__init__(status_code=400, detail="You cannot claim your own item")
