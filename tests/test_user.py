import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me_success(ac: AsyncClient, auth_user):
    response = await ac.get("/api/users/me", headers=auth_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == auth_user["user"]["id"]
    assert data["phone"] == auth_user["user_data"]["phone"]
    assert "password" not in data


@pytest.mark.asyncio
async def test_get_me_unauthorized(ac: AsyncClient):
    response = await ac.get("/api/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_success(ac: AsyncClient, auth_user):
    new_data = {
        "first_name": "NewFirstName",
        "last_name": "NewLastName",
        "bio": "New bio"
    }
    response = await ac.patch("/api/users/update", json=new_data, headers=auth_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "NewFirstName"
    assert data["last_name"] == "NewLastName"
    assert data["bio"] == "New bio"
    assert data["phone"] == auth_user["user_data"]["phone"]


@pytest.mark.asyncio
async def test_update_profile_partial(ac: AsyncClient, auth_user):
    response = await ac.patch("/api/users/update", json={"bio": "Just bio"}, headers=auth_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == "Just bio"
    assert data["first_name"] == auth_user["user_data"]["first_name"]


@pytest.mark.asyncio
async def test_update_profile_duplicate_phone(ac: AsyncClient, auth_user, another_auth_user):
    response = await ac.patch("/api/users/update",
                              json={"phone": another_auth_user["user_data"]["phone"]},
                              headers=auth_user["headers"])
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_user_success(ac: AsyncClient, user_data):
    # Регистрация и логин
    await ac.post("/api/auth/register", json=user_data)
    login_resp = await ac.post("/api/auth/login", json={
        "phone": user_data["phone"],
        "password": user_data["password"]
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    delete_data = {"password": user_data["password"]}
    response = await ac.request("DELETE", "/api/users/delete", json=delete_data, headers=headers)
    assert response.status_code == 204

    # Проверка, что вход невозможен
    login_resp2 = await ac.post("/api/auth/login", json={
        "phone": user_data["phone"],
        "password": user_data["password"]
    })
    assert login_resp2.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_wrong_password(ac: AsyncClient, auth_user):
    delete_data = {"password": "wrongpassword"}
    response = await ac.request("DELETE", "/api/users/delete", json=delete_data, headers=auth_user["headers"])
    assert response.status_code == 400
    assert "invalid password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_user_unauthorized(ac: AsyncClient):
    response = await ac.request("DELETE", "/api/users/delete", json={"password": "any"})
    assert response.status_code == 401