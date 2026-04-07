from app.exceptions import AppException


class InvalidCredentials(AppException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Invalid credentials")


class UserAlreadyExists(AppException):
    def __init__(self) -> None:
        super().__init__(status_code=409, detail="User with this email already exists")


class InvalidToken(AppException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Invalid or expired token")
