from httpx import AsyncClient

BASE = "/api/v1/auth"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _register(client: AsyncClient, email: str = "user@example.com", password: str = "Password1", full_name: str = "Test User") -> dict:
    response = await client.post(f"{BASE}/register", json={"email": email, "password": password, "full_name": full_name})
    return response


async def _login(client: AsyncClient, email: str = "user@example.com", password: str = "Password1") -> dict:
    response = await client.post(f"{BASE}/login", json={"email": email, "password": password})
    return response


async def _auth_headers(client: AsyncClient) -> dict:
    await _register(client)
    res = await _login(client)
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

async def test_register_success(client: AsyncClient):
    res = await _register(client)
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "user@example.com"
    assert body["is_active"] is True
    assert "id" in body
    assert "password" not in body
    assert "hashed_password" not in body


async def test_register_duplicate_email(client: AsyncClient):
    await _register(client)
    res = await _register(client)
    assert res.status_code == 409


async def test_register_password_too_short(client: AsyncClient):
    res = await _register(client, password="Abc1")
    assert res.status_code == 422


async def test_register_password_no_uppercase(client: AsyncClient):
    res = await _register(client, password="password1")
    assert res.status_code == 422


async def test_register_password_no_digit(client: AsyncClient):
    res = await _register(client, password="Password")
    assert res.status_code == 422


async def test_register_invalid_email(client: AsyncClient):
    res = await _register(client, email="not-an-email")
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

async def test_login_success(client: AsyncClient):
    await _register(client)
    res = await _login(client)
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    await _register(client)
    res = await _login(client, password="WrongPass1")
    assert res.status_code == 401


async def test_login_unknown_email(client: AsyncClient):
    res = await _login(client, email="nobody@example.com")
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# Me
# ---------------------------------------------------------------------------

async def test_get_me_success(client: AsyncClient):
    headers = await _auth_headers(client)
    res = await client.get(f"{BASE}/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "user@example.com"


async def test_get_me_no_token(client: AsyncClient):
    res = await client.get(f"{BASE}/me")
    assert res.status_code == 401


async def test_get_me_invalid_token(client: AsyncClient):
    res = await client.get(f"{BASE}/me", headers={"Authorization": "Bearer bogus"})
    assert res.status_code == 401


async def test_get_me_refresh_token_rejected(client: AsyncClient):
    await _register(client)
    login_res = await _login(client)
    refresh_token = login_res.json()["refresh_token"]
    res = await client.get(f"{BASE}/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# Change password
# ---------------------------------------------------------------------------

async def test_change_password_success(client: AsyncClient):
    headers = await _auth_headers(client)
    res = await client.put(
        f"{BASE}/change-password",
        json={"current_password": "Password1", "new_password": "NewPassword2"},
        headers=headers,
    )
    assert res.status_code == 200

    # Can log in with new password
    login_res = await _login(client, password="NewPassword2")
    assert login_res.status_code == 200


async def test_change_password_wrong_current(client: AsyncClient):
    headers = await _auth_headers(client)
    res = await client.put(
        f"{BASE}/change-password",
        json={"current_password": "WrongPass1", "new_password": "NewPassword2"},
        headers=headers,
    )
    assert res.status_code == 401


async def test_change_password_no_token(client: AsyncClient):
    res = await client.put(
        f"{BASE}/change-password",
        json={"current_password": "Password1", "new_password": "NewPassword2"},
    )
    assert res.status_code == 401


async def test_change_password_weak_new_password(client: AsyncClient):
    headers = await _auth_headers(client)
    res = await client.put(
        f"{BASE}/change-password",
        json={"current_password": "Password1", "new_password": "weak"},
        headers=headers,
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------

async def test_refresh_success(client: AsyncClient):
    await _register(client)
    login_res = await _login(client)
    refresh_token = login_res.json()["refresh_token"]

    res = await client.post(f"{BASE}/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_refresh_access_token_rejected(client: AsyncClient):
    await _register(client)
    login_res = await _login(client)
    access_token = login_res.json()["access_token"]

    res = await client.post(f"{BASE}/refresh", json={"refresh_token": access_token})
    assert res.status_code == 401


async def test_refresh_invalid_token(client: AsyncClient):
    res = await client.post(f"{BASE}/refresh", json={"refresh_token": "garbage"})
    assert res.status_code == 401


async def test_refresh_new_access_token_is_usable(client: AsyncClient):
    await _register(client)
    login_res = await _login(client)
    refresh_token = login_res.json()["refresh_token"]

    refresh_res = await client.post(f"{BASE}/refresh", json={"refresh_token": refresh_token})
    new_access_token = refresh_res.json()["access_token"]

    me_res = await client.get(f"{BASE}/me", headers={"Authorization": f"Bearer {new_access_token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "user@example.com"


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

async def test_rate_limit_login(client: AsyncClient):
    await _register(client)
    for _ in range(5):
        await _login(client)

    res = await _login(client)
    assert res.status_code == 429


async def test_rate_limit_register(client: AsyncClient):
    for i in range(5):
        await _register(client, email=f"user{i}@example.com")

    res = await _register(client, email="extra@example.com")
    assert res.status_code == 429
