from app.exceptions import AppException


class MatchNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(status_code=404, detail="Match not found")
