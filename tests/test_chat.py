import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_chats_empty(ac: AsyncClient, auth_user):
    """Пользователь без чатов получает пустой список"""
    resp = await ac.get("/api/chats/", headers=auth_user["headers"])
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_private_chat_success(ac: AsyncClient, auth_user, another_auth_user):
    """Создание личного чата между двумя пользователями"""
    other_id = another_auth_user["user"]["id"]
    resp = await ac.post(
        "/api/chats/private",
        json={"other_user_id": other_id},
        headers=auth_user["headers"]
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["other_user_id"] == other_id


@pytest.mark.asyncio
async def test_create_private_chat_self(ac: AsyncClient, auth_user):
    """Попытка создать чат с самим собой -> 400"""
    resp = await ac.post(
        "/api/chats/private",
        json={"other_user_id": auth_user["user"]["id"]},
        headers=auth_user["headers"]
    )
    assert resp.status_code == 400
    assert "yourself" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_private_chat_user_not_found(ac: AsyncClient, auth_user):
    """Несуществующий пользователь -> 400"""
    resp = await ac.post(
        "/api/chats/private",
        json={"other_user_id": 99999},
        headers=auth_user["headers"]
    )
    assert resp.status_code == 400
    assert "not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_group_chat_success(ac: AsyncClient, auth_user, another_auth_user):
    """Создание группового чата с двумя участниками"""
    participants = [another_auth_user["user"]["id"]]
    payload = {
        "name": "Test Group",
        "participants_ids": participants,
        "avatar": None
    }
    resp = await ac.post("/api/chats/group", json=payload, headers=auth_user["headers"])
    print(resp.json(), resp.status_code)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Group"
    assert data["creator_id"] == auth_user["user"]["id"]
    assert auth_user["user"]["id"] in data["participants_ids"]
    assert another_auth_user["user"]["id"] in data["participants_ids"]
    assert len(data["participants_ids"]) == 2


@pytest.mark.asyncio
async def test_create_group_chat_invalid_user(ac: AsyncClient, auth_user):
    """Создание группы с несуществующим участником -> 400"""
    payload = {
        "name": "Bad Group",
        "participants_ids": [99999],
        "avatar": None
    }
    resp = await ac.post("/api/chats/group", json=payload, headers=auth_user["headers"])
    assert resp.status_code == 400
    assert "не существуют" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_chats_after_creation(ac: AsyncClient, auth_user, another_auth_user):
    """После создания чатов они появляются в списке"""
    # Создаём личный чат
    await ac.post("/api/chats/private", json={"other_user_id": another_auth_user["user"]["id"]}, headers=auth_user["headers"])
    # Создаём групповой чат
    await ac.post("/api/chats/group", json={"name": "Group", "participants_ids": [another_auth_user["user"]["id"]]}, headers=auth_user["headers"])

    resp = await ac.get("/api/chats/", headers=auth_user["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    # Проверяем, что тип определён
    types = [chat["type"] for chat in data]
    assert "chat" in types or "private" in types  # в зависимости от твоей реализации
    assert "group" in types


@pytest.mark.asyncio
async def test_soft_delete_chat(ac: AsyncClient, auth_user, another_auth_user):
    """Мягкое удаление чата у пользователя"""
    # Создаём чат
    create_resp = await ac.post("/api/chats/private", json={"other_user_id": another_auth_user["user"]["id"]}, headers=auth_user["headers"])
    chat_id = create_resp.json()["id"]

    # Удаляем
    del_resp = await ac.delete(f"/api/chats/{chat_id}", headers=auth_user["headers"])
    assert del_resp.status_code == 204

    # Список чатов пользователя должен быть пуст
    chats = await ac.get("/api/chats/", headers=auth_user["headers"])
    assert chats.json() == []

    # Другой пользователь всё ещё видит чат
    other_chats = await ac.get("/api/chats/", headers=another_auth_user["headers"])
    assert len(other_chats.json()) == 1


@pytest.mark.asyncio
async def test_soft_delete_not_participant(ac: AsyncClient, auth_user, another_auth_user):
    """Попытка удалить чат, в котором пользователь не участвует -> 404"""
    # Создаём чат между auth_user и another_auth_user
    create_resp = await ac.post("/api/chats/private", json={"other_user_id": another_auth_user["user"]["id"]}, headers=auth_user["headers"])
    chat_id = create_resp.json()["id"]

    # Пытаемся удалить от третьего пользователя (создаём третьего)
    third_data = {
        "phone": "+79657357259999",
        "username": "third",
        "first_name": "Third",
        "password": "third123"
    }
    await ac.post("/api/auth/register", json=third_data)
    login = await ac.post("/api/auth/login", json={"phone": third_data["phone"], "password": third_data["password"]})
    third_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    del_resp = await ac.delete(f"/api/chats/{chat_id}", headers=third_headers)
    assert del_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_group_chat_by_creator(ac: AsyncClient, auth_user, another_auth_user):
    """Создатель может полностью удалить групповой чат"""
    # Создаём группу
    payload = {
        "name": "ToDelete",
        "participants_ids": [another_auth_user["user"]["id"]],
        "avatar": None
    }
    create_resp = await ac.post("/api/chats/group", json=payload, headers=auth_user["headers"])
    chat_id = create_resp.json()["id"]

    # Удаляем группой
    del_resp = await ac.delete(f"/api/chats/group/{chat_id}", headers=auth_user["headers"])
    assert del_resp.status_code == 204

    # Проверяем, что чат исчез у обоих
    chats_auth = await ac.get("/api/chats/", headers=auth_user["headers"])
    assert chats_auth.json() == []
    chats_other = await ac.get("/api/chats/", headers=another_auth_user["headers"])
    assert chats_other.json() == []


@pytest.mark.asyncio
async def test_delete_group_chat_not_creator(ac: AsyncClient, auth_user, another_auth_user):
    """Не создатель не может удалить группу -> 403"""
    # Создаём группу
    payload = {
        "name": "Protected",
        "participants_ids": [another_auth_user["user"]["id"]],
        "avatar": None
    }
    create_resp = await ac.post("/api/chats/group", json=payload, headers=auth_user["headers"])
    chat_id = create_resp.json()["id"]

    # Другой пользователь пытается удалить
    del_resp = await ac.delete(f"/api/chats/group/{chat_id}", headers=another_auth_user["headers"])
    assert del_resp.status_code == 403


@pytest.mark.asyncio
async def test_update_group_chat_success(ac: AsyncClient, auth_user, another_auth_user):
    """Создатель может обновить название и описание группы"""
    # Создаём группу
    payload = {
        "name": "Original Name",
        "participants_ids": [another_auth_user["user"]["id"]],
        "avatar": None
    }
    create_resp = await ac.post("/api/chats/group", json=payload, headers=auth_user["headers"])
    chat_id = create_resp.json()["id"]

    # Обновляем
    update_data = {"name": "New Name", "description": "Cool description"}
    patch_resp = await ac.patch(f"/api/chats/{chat_id}", json=update_data, headers=auth_user["headers"])
    print(patch_resp.status_code, patch_resp.json())
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["name"] == "New Name"
    assert data["description"] == "Cool description"


@pytest.mark.asyncio
async def test_update_group_chat_not_creator(ac: AsyncClient, auth_user, another_auth_user):
    """Не создатель не может обновить группу -> 403"""
    payload = {
        "name": "Group",
        "participants_ids": [another_auth_user["user"]["id"]],
        "avatar": None
    }
    create_resp = await ac.post("/api/chats/group", json=payload, headers=auth_user["headers"])
    chat_id = create_resp.json()["id"]

    update_data = {"name": "Hacked"}
    patch_resp = await ac.patch(f"/api/chats/{chat_id}", json=update_data, headers=another_auth_user["headers"])
    assert patch_resp.status_code == 403


@pytest.mark.asyncio
async def test_update_group_chat_not_found(ac: AsyncClient, auth_user):
    """Обновление несуществующего чата -> 404"""
    patch_resp = await ac.patch("/api/chats/99999", json={"name": "New"}, headers=auth_user["headers"])
    assert patch_resp.status_code == 404


@pytest.mark.asyncio
async def test_update_private_chat_should_fail(ac: AsyncClient, auth_user, another_auth_user):
    """Обновление личного чата (не группы) -> 400 или 404"""
    # Создаём личный чат
    create_resp = await ac.post("/api/chats/private", json={"other_user_id": another_auth_user["user"]["id"]}, headers=auth_user["headers"])
    chat_id = create_resp.json()["id"]

    patch_resp = await ac.patch(f"/api/chats/{chat_id}", json={"name": "Try"}, headers=auth_user["headers"])
    # По логике, должно быть 400 (не группой) или 404
    assert patch_resp.status_code in [400, 404]