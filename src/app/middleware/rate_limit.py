import time
from collections import defaultdict

from fastapi import Request

from app.exceptions import RateLimitExceeded


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def _clean_old_requests(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self.requests[key] = [t for t in self.requests[key] if t > cutoff]

    async def check(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        self._clean_old_requests(client_ip, now)

        if len(self.requests[client_ip]) >= self.max_requests:
            raise RateLimitExceeded()

        self.requests[client_ip].append(now)


rate_limiter = RateLimiter()
