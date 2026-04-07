import pytest


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from app.auth.router import auth_rate_limiter

    auth_rate_limiter.requests.clear()
    yield
    auth_rate_limiter.requests.clear()
