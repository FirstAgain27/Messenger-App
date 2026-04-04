import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_message_success(ac: AsyncClient, auth_user, private_chat_id):
    """Отправка сообщения в личный чат"""
    message_data = {"chat_id": private_chat_id, "text": "Hello from test"}
    resp = await ac.post("/api/messages/", json=message_data, headers=auth_user["headers"])
    assert resp.status_code == 201
    data = resp.json()
    assert data["chat_id"] == private_chat_id
    assert data["sender_id"] == auth_user["user"]["id"]
    assert data["text"] == "Hello from test"


@pytest.mark.asyncio
async def test_send_message_not_participant(ac: AsyncClient, private_chat_id):
    """Попытка отправить сообщение от пользователя, не участвующего в чате"""
    # Создаём третьего пользователя
    third_data = {
        "phone": "+79657357259999",
        "username": "thirduser",
        "first_name": "Third",
        "password": "third123"
    }
    reg = await ac.post("/api/auth/register", json=third_data)
    assert reg.status_code == 201
    login = await ac.post("/api/auth/login", json={
        "phone": third_data["phone"],
        "password": third_data["password"]
    })
    third_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = await ac.post("/api/messages/", json={"chat_id": private_chat_id, "text": "Hi"}, headers=third_headers)
    assert resp.status_code == 403
    assert "участником" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_send_message_chat_not_found(ac: AsyncClient, auth_user):
    resp = await ac.post("/api/messages/", json={"chat_id": 99999, "text": "Hi"}, headers=auth_user["headers"])
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_chat_history(ac: AsyncClient, auth_user, private_chat_id):
    # Отправляем три сообщения
    for i in range(3):
        await ac.post("/api/messages/", json={"chat_id": private_chat_id, "text": f"Msg{i}"}, headers=auth_user["headers"])

    resp = await ac.get(f"/api/messages/{private_chat_id}", headers=auth_user["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert data[0]["text"] == "Msg0"


@pytest.mark.asyncio
async def test_get_chat_history_pagination(ac: AsyncClient, auth_user, private_chat_id):
    for i in range(10):
        await ac.post("/api/messages/", json={"chat_id": private_chat_id, "text": f"Msg{i}"}, headers=auth_user["headers"])

    resp = await ac.get(f"/api/messages/{private_chat_id}?limit=5&offset=0", headers=auth_user["headers"])
    assert len(resp.json()) == 5
    assert resp.json()[0]["text"] == "Msg0"

    resp = await ac.get(f"/api/messages/{private_chat_id}?limit=5&offset=5", headers=auth_user["headers"])
    assert len(resp.json()) == 5
    assert resp.json()[0]["text"] == "Msg5"


@pytest.mark.asyncio
async def test_get_chat_history_not_participant(ac: AsyncClient, private_chat_id):
    # Создаём третьего пользователя
    third_data = {
        "phone": "+79657357259888",
        "username": "third2",
        "first_name": "Third2",
        "password": "third456"
    }
    await ac.post("/api/auth/register", json=third_data)
    login = await ac.post("/api/auth/login", json={
        "phone": third_data["phone"],
        "password": third_data["password"]
    })
    third_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = await ac.get(f"/api/messages/{private_chat_id}", headers=third_headers)
    assert resp.status_code == 403
    assert "участником" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_message_success(ac: AsyncClient, auth_user, private_chat_id):
    send = await ac.post("/api/messages/", json={"chat_id": private_chat_id, "text": "To delete"}, headers=auth_user["headers"])
    msg_id = send.json()["id"]

    del_resp = await ac.delete(f"/api/messages/{msg_id}", headers=auth_user["headers"])
    assert del_resp.status_code == 204

    history = await ac.get(f"/api/messages/{private_chat_id}", headers=auth_user["headers"])
    assert len(history.json()) == 0


@pytest.mark.asyncio
async def test_delete_message_other_user(ac: AsyncClient, auth_user, another_auth_user, private_chat_id):
    # Отправляем сообщение от auth_user
    send = await ac.post("/api/messages/", json={"chat_id": private_chat_id, "text": "Auth's message"}, headers=auth_user["headers"])
    msg_id = send.json()["id"]

    # Пытаемся удалить от another_auth_user
    del_resp = await ac.delete(f"/api/messages/{msg_id}", headers=another_auth_user["headers"])
    assert del_resp.status_code == 403
    assert "чужие" in del_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_message_not_found(ac: AsyncClient, auth_user):
    resp = await ac.delete("/api/messages/99999", headers=auth_user["headers"])
    assert resp.status_code == 404