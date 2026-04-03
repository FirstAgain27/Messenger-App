import os
import pytest
from httpx import AsyncClient, ASGITransport

# Тестовые переменные
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["encryption_key"] = "75S-s7-A6_p93_3y123456789012345678901234567="

from app.main import app
from app.core.database import engine, Base

@pytest.fixture
async def ac():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def user_data():
    import time
    unique = int(time.time() * 1000) % 100000
    return {
        "phone": f"+79657357259{unique:05d}"[-15:],
        "username": f"testuser{unique}",
        "first_name": "Test",
        "password": "testpass123"
    } 

@pytest.fixture
async def auth_user(ac: AsyncClient, user_data):
    """Регистрирует пользователя и возвращает заголовки, данные пользователя и его ID."""
    reg_resp = await ac.post("/api/auth/register", json=user_data)
    assert reg_resp.status_code == 201
    user = reg_resp.json()
    login_resp = await ac.post("/api/auth/login", json={
        "phone": user_data["phone"],
        "password": user_data["password"]
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return {"headers": headers, "user": user, "user_data": user_data}

@pytest.fixture
def another_user_data():
    import time
    unique = (int(time.time() * 1000) + 100000) % 100000
    return {
        "phone": f"+79657357259{unique:05d}"[-15:],
        "username": f"another{unique}",
        "first_name": "Another",
        "password": "another123"
    }

@pytest.fixture
async def another_auth_user(ac: AsyncClient, another_user_data):
    """Второй пользователь для тестов конфликтов."""
    reg_resp = await ac.post("/api/auth/register", json=another_user_data)
    assert reg_resp.status_code == 201
    user = reg_resp.json()
    login_resp = await ac.post("/api/auth/login", json={
        "phone": another_user_data["phone"],
        "password": another_user_data["password"]
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return {"headers": headers, "user": user, "user_data": another_user_data}